/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2024, the respective contributors. All rights reserved.
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

using BH.oM.Base;
using BH.oM.Base.Attributes;
using BH.oM.Python;
using BH.oM.Python.Enums;
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
        [Output("stdout", "The StandardOutput from the command that was run. If the process failed, then StandardError will be returned here instead.")]
        public static string RunCommandStdout(string command, bool hideWindows = true, string startDirectory = null, double timeoutMinutes = 5)
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

            int millisecondsToWait = (int)timeoutMinutes * 60 * 1000;
            process.WaitForExit(millisecondsToWait);

            if (process.ExitCode != 0)
            {
                return stderr.Trim();
            }

            return stdout.Trim();
        }

        [Description("Run a string containing Python code and return the output. The string passed should end with a \"print\" statement, and other print statements within it should be captured within the script to ensure only a single output string is passed back to this method.")]
        [Input("env", "The Python environment with which to run the Python script.")]
        [Input("pythonString", "The string containing the Python script.")]
        [Output("result", "The stdout data from the executed Python script.")]
        public static string RunPythonString(this oM.Python.PythonEnvironment env, string pythonString)
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

            string cmd = $"{Modify.AddQuotesIfRequired(env.Executable)} {scriptFile}";

            return RunCommandStdout(cmd, hideWindows: true);
        }
    }
}

