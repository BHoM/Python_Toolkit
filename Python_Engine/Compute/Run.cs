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
        [Description("Run a command via CMD and return stdout.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        [Input("timeoutMinutes", "A number of minutes beyond which this command will timeout.")]
        [Output("stdout", "The StandardOutput from the command that was run, if the process was successful.")]
        public static string RunCommandStdout(
            string command,
            bool hideWindow = true,
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

            var process = new Process();

            try
            {
                process.StartInfo.FileName = "cmd.exe";
                process.StartInfo.Arguments = string.Format("/C \"{0}\"", command);
                process.StartInfo.WorkingDirectory = startDirectory;

                process.StartInfo.UseShellExecute = false;
                process.StartInfo.RedirectStandardOutput = true;
                process.StartInfo.RedirectStandardError = true;
                process.StartInfo.CreateNoWindow = hideWindow;
                process.StartInfo.WindowStyle =
                    hideWindow
                        ? ProcessWindowStyle.Hidden
                        : ProcessWindowStyle.Normal;

                // Avoid environment-variable interference.
                process.StartInfo.EnvironmentVariables["PYTHONHOME"] = string.Empty;
                process.StartInfo.EnvironmentVariables["PYTHONPATH"] = string.Empty;

                process.Start();

                var stdoutTask = process.StandardOutput.ReadToEndAsync();
                var stderrTask = process.StandardError.ReadToEndAsync();

                int timeoutMs = checked((int)(timeoutMinutes * 60 * 1000));

                if (!process.WaitForExit(timeoutMs))
                {
                    try
                    {
                        process.Kill();
                    }
                    catch
                    {
                        // Ignore if already exited.
                    }

                    throw new TimeoutException(
                        string.Format(
                            "Command exceeded timeout of {0} minutes.",
                            timeoutMinutes));
                }

                // Ensure async reads have completed.
                Task.WaitAll(stdoutTask, stderrTask);

                string stdout = stdoutTask.Result.Trim();
                string stderr = stderrTask.Result.Trim();

                int exitCode = process.ExitCode;
                string output = exitCode == 0 ? stdout : stderr;

                if (exitCode != 0)
                {
                    string message = $"Failed to execute {command} (exit code {exitCode}).\n{output}";
                    BH.Engine.Base.Compute.RecordError(
                        exception: new InvalidOperationException(message),
                        message: message);
                }

                return output;

            }
            finally
            {
                process.Dispose();
            }
        }

        [Description("Run a string containing Python code and return the output. The string passed should end with a \"print\" statement, and other print statements within it should be captured within the script to ensure only a single output string is passed back to this method.")]
        [Input("env", "The Python environment with which to run the Python script.")]
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

            return RunCommandStdout(command: cmd);
        }
    }
}
