/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
 *
 * Each contributor holds copyright over their respective contributions.
 * The project versioning (Git) records all such contribution source information.
 *                                           
 *                                                                              
 * The BHoM is free software: you can redistribute it and/or modify         
 * it under the terms of the GNU Lesser General Public License as published by  
 * the Free Software Foundation, either version 3.0 of the License, or          
 * (at your option) any later version.                                          
 *                                                                              
 * The BHoM is distributed in the hope that it will be useful,              
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
 * GNU Lesser General Public License for more details.                          
 *                                                                            
 * You should have received a copy of the GNU Lesser General Public License     
 * along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
 */

using BH.oM.Base.Attributes;
using BH.oM.Base;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Run a command via CMD and return both output streams and the exit code.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        [Input("timeoutMinutes", "A number of minutes beyond which this command will timeout.")]
        [MultiOutput(0, "stdout", "The command's standard output, including on failure.")]
        [MultiOutput(1, "stderr", "The command's standard error, including on success.")]
        [MultiOutput(2, "exitCode", "The process exit code. Zero indicates success; -1 indicates a timeout.")]
        public static Output<string, string, int> RunCommandStdout(
            string command,
            bool hideWindows = true,
            string startDirectory = null,
            double timeoutMinutes = 5
        )
        {
            if (string.IsNullOrWhiteSpace(startDirectory))
            {
                startDirectory = Environment.CurrentDirectory;
            }

            if (!Directory.Exists(startDirectory))
            {
                throw new DirectoryNotFoundException(
                    string.Format("Working directory does not exist: '{0}'", startDirectory));
            }

            using (Process process = new Process())
            {
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = string.Format("/C \"{0}\"", command);
                process.StartInfo.WorkingDirectory = startDirectory;

                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = hideWindows;
                process.StartInfo.WindowStyle = hideWindows ? ProcessWindowStyle.Hidden : ProcessWindowStyle.Normal;

                // Avoid environment-variable interference.
                process.StartInfo.EnvironmentVariables["PYTHONHOME"] = string.Empty;
                process.StartInfo.EnvironmentVariables["PYTHONPATH"] = string.Empty;

                process.Start();

                StreamReader stdoutReader = process.StandardOutput;
                StreamReader stderrReader = process.StandardError;

                // Start reads without inheriting the host's UI synchronization context.
                Task<string[]> outputTask = Task.Run(async () =>
                {
                    Task<string> stdoutTask = stdoutReader.ReadToEndAsync();
                    Task<string> stderrTask = stderrReader.ReadToEndAsync();

                    return await Task.WhenAll(stdoutTask, stderrTask).ConfigureAwait(false);
                });

                int timeoutMs = checked((int)(timeoutMinutes * 60 * 1000));

                bool timedOut = !process.WaitForExit(timeoutMs);
                if (timedOut)
                {
                    // Kill descendants too, so inherited pipe handles cannot keep the reads open.
                    using (Process terminator = Process.Start(new ProcessStartInfo
                    {
                        FileName = "taskkill.exe",
                        Arguments = $"/PID {process.Id} /T /F",
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true
                    }))
                    {
                        Task<string> killStdout = terminator.StandardOutput.ReadToEndAsync();
                        Task<string> killStderr = terminator.StandardError.ReadToEndAsync();
                        terminator.WaitForExit();
                        Task.WaitAll(killStdout, killStderr);
                        if (terminator.ExitCode != 0 && !process.HasExited)
                            throw new InvalidOperationException($"Could not terminate timed-out command: {killStderr.GetAwaiter().GetResult()}");
                    }
                    process.WaitForExit();
                    BH.Engine.Base.Compute.RecordError(new TimeoutException(), $"Command exceeded timeout of {timeoutMinutes} minutes.\nCommand: {command}");
                }

                // Ensure async reads have completed.
                string[] results = outputTask.GetAwaiter().GetResult();

                string stdout = results[0].Trim();
                string stderr = results[1].Trim();

                int exitCode = timedOut ? -1 : process.ExitCode;

                if (!timedOut && exitCode != 0)
                {
                    string message = $"Failed to execute {command} (exit code {exitCode}).\n{stdout}\n{stderr}";
                    BH.Engine.Base.Compute.RecordError(
                        exception: new InvalidOperationException(message),
                        message: message);
                }

                return new Output<string, string, int> { Item1 = stdout, Item2 = stderr, Item3 = exitCode };
            }
        }

        [Description("Run a string containing Python code and return the output. The string passed should end with a \"print\" statement, and other print statements within it should be captured within the script to ensure only a single output string is passed back to this method.")]
        [Input("venv", "The Python environment with which to run the Python script.")]
        [Input("pythonString", "The string containing the Python script.")]
        [Output("result", "The stdout data from the executed Python script.")]
        public static string RunPythonString(this oM.Python.PythonEnvironment venv, string pythonString)
        {
            if (!pythonString.Split('\n').Last().Contains("print"))
            {
                BH.Engine.Base.Compute.RecordWarning("Nothing is being passed to StdOut in the Python script, so nothing will be returned from this method.");
            }

            // place pythonScript into a temporary .py file to reference and run, then call using the passed environment
            string scriptFile = Path.Combine(Path.GetTempPath(), "_BHoM_PythonScript.py");
            using (StreamWriter outputFile = new StreamWriter(scriptFile))
            {
                outputFile.WriteLine(pythonString);
            }

            string cmd = $"{Modify.AddQuotesIfRequired(venv.Executable)} {scriptFile}";

            Output<string, string, int> result = RunCommandStdout(command: cmd);
            return result.Item3 == 0 ? result.Item1 : result.Item2;
        }
    }
}
