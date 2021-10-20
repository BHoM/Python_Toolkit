///*
// * This file is part of the Buildings and Habitats object Model (BHoM)
// * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
// *
// * Each contributor holds copyright over their respective contributions.
// * The project versioning (Git) records all such contribution source information.
// *                                           
// *                                                                              
// * The BHoM is free software: you can redistribute it and/or modify         
// * it under the terms of the GNU Lesser General Public License as published by  
// * the Free Software Foundation, either version 3.0 of the License, or          
// * (at your option) any later version.                                          
// *                                                                              
// * The BHoM is distributed in the hope that it will be useful,              
// * but WITHOUT ANY WARRANTY; without even the implied warranty of               
// * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
// * GNU Lesser General Public License for more details.                          
// *                                                                            
// * You should have received a copy of the GNU Lesser General Public License     
// * along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
// */

//using BH.oM.Reflection.Attributes;
//using System.Collections.Generic;
//using System.ComponentModel;
//using System.IO;
//using System.Threading.Tasks;

//namespace BH.Engine.Python
//{
//    public static partial class Compute
//    {
//        /***************************************************/
//        /**** Public Methods                            ****/
//        /***************************************************/

//        [Description("Run a command via CMD and return stdout.")]
//        [Input("command", "The command to be run.")]
//        [Input("hideWindows", "Set to True to hide cmd windows.")]
//        [Input("startDirectory", "The directory in which the command should be run.")]
//        [Output("stdout", "The StdOut from the command that was run.")]
//        public static string RunCommand(string command, bool hideWindows = false, string startDirectory = null)
//        {
//            System.Diagnostics.Process process = new System.Diagnostics.Process();

//            string commandMode = "/K";
//            if (hideWindows)
//            {
//                process.StartInfo.CreateNoWindow = true;
//                process.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
//                commandMode = "/C";
//            }
//            process.StartInfo.FileName = "cmd.exe";
//            process.StartInfo.RedirectStandardOutput = true;
//            process.StartInfo.UseShellExecute = false;
//            process.StartInfo.WorkingDirectory = startDirectory ?? Query.EmbeddedPythonHome();
//            process.StartInfo.Arguments = $"{commandMode} {command}";
//            process.Start();

//            // To avoid deadlocks, always read the output stream first and then wait.  
//            string stdout = process.StandardOutput.ReadToEnd();
//            string stderr = process.StandardError.ReadToEnd();
//            process.WaitForExit();

//            if (process.ExitCode != 0)
//            {
//                return stderr;
//            }

//            return stdout;
//        }

//        /***************************************************/

//        [Description("Run the given command asynchronously via CMD.")]
//        [Input("command", "The command to be run.")]
//        [Input("hideWindows", "Set to True to hide cmd windows.")]
//        [Input("startDirectory", "The directory in which the command should be run.")]
//        public static async void RunCommandAsync(string command, bool hideWindows = true, string startDirectory = null)
//        {
//            await Task.Run(() =>
//            {
//                System.Diagnostics.Process process = new System.Diagnostics.Process();
//                System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();

//                if (hideWindows)
//                    startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
//                string commandMode = hideWindows ? "/C" : "/K";

//                startInfo.FileName = "cmd.exe";
//                startInfo.WorkingDirectory = startDirectory ?? Query.EmbeddedPythonHome();
//                startInfo.Arguments = $"{commandMode} {command} && exit";

//                process.StartInfo = startInfo;
//                process.Start();
//            });
//        }

//        /***************************************************/
//    }
//}

