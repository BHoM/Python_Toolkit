/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2020, the respective contributors. All rights reserved.
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

using System.Threading;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static void RunCommand(string command, bool hideWindows = false, string startDirectory = null)
        {
            System.Diagnostics.Process process = new System.Diagnostics.Process();
            System.Diagnostics.ProcessStartInfo startInfo = new System.Diagnostics.ProcessStartInfo();

            if (hideWindows)
                startInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            string commandMode = hideWindows ? "/C" : "/K";

            startInfo.FileName = "cmd.exe";
            startInfo.WorkingDirectory = startDirectory ?? Query.EmbeddedPythonHome();
            startInfo.Arguments = $"{commandMode} {command} & exit";

            process.StartInfo = startInfo;
            process.Start();
            process.WaitForExit();
        }

        /***************************************************/

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
                startInfo.Arguments = $"{commandMode} {command} & exit";

                process.StartInfo = startInfo;
                process.Start();
            });
        }

        /***************************************************/
    }
}
