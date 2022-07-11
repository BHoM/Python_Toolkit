/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2022, the respective contributors. All rights reserved.
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
using System.Threading;
using System.Threading.Tasks;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Run a command via CMD and return stdout.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        [Output("stdout", "The StandardOutput from the command that was run. If the process failed, then StandardError will be returned here instead.")]
        public static async void RunCommandAsync(string command, bool hideWindows = true, string startDirectory = null)
        {
            await Task.Run(() =>
            {
                System.Diagnostics.Process process = new System.Diagnostics.Process();
                System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();

                string commandMode = "/K";
                if (hideWindows)
                {
                    startInfo.CreateNoWindow = true;
                    startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
                    commandMode = "/C";
                }

                startInfo.FileName = "cmd.exe";
                startInfo.RedirectStandardOutput = true;
                startInfo.RedirectStandardError = true;
                startInfo.UseShellExecute = false;
                startInfo.Arguments = $"{commandMode} {command} && exit";

                process.StartInfo = startInfo;
                process.Start();
            });
        }

        [Description("Run a command via CMD and return True if successful and False if not.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        [Output("success", "True if successful and False if not.")]
        public static bool RunCommandBool(string command, bool hideWindows = false, string startDirectory = null)
        {
            System.Diagnostics.Process process = new System.Diagnostics.Process();

            string commandMode = "/K";
            if (hideWindows)
            {
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
                commandMode = "/C";
            }
            process.StartInfo.FileName = "cmd.exe";
            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.Arguments = $"{commandMode} {command}";
            process.Start();

            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                return false;
            }

            return true;
        }

        [Description("Run a command via CMD and return stdout.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        [Output("stdout", "The StandardOutput from the command that was run. If the process failed, then StandardError will be returned here instead.")]
        public static string RunCommandStdout(string command, bool hideWindows = true, string startDirectory = null)
        {
            System.Diagnostics.Process process = new System.Diagnostics.Process();

            string commandMode = "/K";
            if (hideWindows)
            {
                process.StartInfo.CreateNoWindow = true;
                process.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
                commandMode = "/C";
            }
            process.StartInfo.FileName = "cmd.exe";
            process.StartInfo.RedirectStandardOutput = true;
            process.StartInfo.RedirectStandardError = true;
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.Arguments = $"{commandMode} {command}";
            process.Start();

            // To avoid deadlocks, always read the output stream first and then wait.  
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                return stderr.Trim();
            }

            return stdout.Trim();
        }

        [Description("Run a string containing Python code and return the output.")]
        [Input("env", "The Python environment with which to run the Python script.")]
        [Input("pythonString", "The string containing the Python script.")]
        [Output("result", "The stdout data from the executed Python script.")]
        public static string RunCommandPythonString(this oM.Python.PythonEnvironment env, string pythonString)
        {
            if (!pythonString.Contains("print"))
            {
                BH.Engine.Base.Compute.RecordWarning("Nothing is being passed to StdOut in the Python script, so nothing will be returned from this method.");
            }

            // place pythonScript into a temporary .py file to reference and run, then call using the passed environment
            string scriptFile = Path.Combine(Path.GetTempPath(), "_BHoM_PythonScript.py");
            using (StreamWriter outputFile = new StreamWriter(scriptFile))
            {
                outputFile.WriteLine(pythonString);
            }

            string cmd = $"{Modify.AddQuotesIfRequired(env.Executable)} {scriptFile}";

            string results = RunCommandStdout(cmd, hideWindows: true);

            return results;
        }
    }
}
