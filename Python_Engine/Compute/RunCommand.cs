/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
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

using BH.oM.Reflection.Attributes;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Run the given command via CMD.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        public static void RunCommand(string command, bool hideWindows = false, string startDirectory = null)
        {
            System.Diagnostics.Process process = new System.Diagnostics.Process();
            System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();

            if (hideWindows)
                startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            string commandMode = hideWindows ? "/C" : "/K";

            startInfo.FileName = "cmd.exe";
            startInfo.WorkingDirectory = startDirectory ?? Query.EmbeddedPythonHome();
            startInfo.Arguments = $"{commandMode} {command} && exit";

            process.StartInfo = startInfo;
            process.Start();
            process.WaitForExit();
        }

        /***************************************************/

        [Description("Run a Python script from the given environment, with the arguments given.")]
        [Input("environmentName", "The environment with which to run the Python script.")]
        [Input("pythonScript", "The full path to the Python script.")]
        [Input("args", "Set to True to hide cmd windows.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Output("result", "The data returned by the Python script.")]
        public static string RunCommand(string environmentName, string pythonScript, List<string> args = null, bool hideWindows = true)
        {
            // check that environment exists
            if (!environmentName.VirtualEnvironmentExists())
            {
                return "";
            }

            // Check that script exists at given path
            if (!File.Exists(pythonScript))
            {
                BH.Engine.Reflection.Compute.RecordError($"Python script does not exist at {pythonScript}.");
            }

            // construct command to be run
            string cmd = $"{environmentName.VirtualEnvironmentExecutable()} {pythonScript} {string.Join(" ", args)}";

            // create new process and run script
            System.Diagnostics.Process p = new System.Diagnostics.Process();
            
            string commandMode = hideWindows ? "/C" : "/K";
            if (hideWindows)
            {
                p.StartInfo.CreateNoWindow = true;
                p.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            }
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.FileName = "cmd.exe";
            p.StartInfo.Arguments = $"{commandMode} {cmd}";
            p.Start();

            // To avoid deadlocks, always read the output stream first and then wait.  
            string output = p.StandardOutput.ReadToEnd();
            p.WaitForExit();

            return output;
        }

        /***************************************************/

        [Description("Run the given command asynchronously via CMD.")]
        [Input("command", "The command to be run.")]
        [Input("hideWindows", "Set to True to hide cmd windows.")]
        [Input("startDirectory", "The directory in which the command should be run.")]
        public static async void RunCommandAsync(string command, bool hideWindows = true, string startDirectory = null)
        {
            await Task.Run(() =>
            {
                System.Diagnostics.Process process = new System.Diagnostics.Process();
                System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();

                if (hideWindows)
                    startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
                string commandMode = hideWindows ? "/C" : "/K";

                startInfo.FileName = "cmd.exe";
                startInfo.WorkingDirectory = startDirectory ?? Query.EmbeddedPythonHome();
                startInfo.Arguments = $"{commandMode} {command} && exit";

                process.StartInfo = startInfo;
                process.Start();
            });
        }

        /***************************************************/
    }
}

