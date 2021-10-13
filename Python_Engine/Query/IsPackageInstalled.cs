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

using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Return True if named Python package is installed in given environment.")]
        public static bool IsPackageInstalled(string package, string environmentName = null)
        {
            // get the associated executable with which to run Pip
            string environmentExecutable = Query.EmbeddedPythonExecutable();
            if (environmentName == null)
            {
                BH.Engine.Reflection.Compute.RecordNote("Checking for existence of {package} in the base BHoM Python environment.");
            }
            else
            {
                if (!environmentName.IsVirtualEnvironmentInstalled())
                {
                    return false;
                }
                environmentExecutable = environmentName.VirtualEnvironmentExecutable();
            }

            // run check
            string cmd = $"{environmentExecutable} -m pip show {package}";
            System.Diagnostics.Process p = new System.Diagnostics.Process();
            p.StartInfo.CreateNoWindow = true;
            p.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.FileName = "cmd.exe";
            p.StartInfo.Arguments = $"/C {cmd}";
            p.Start();

            // To avoid deadlocks, always read the output stream first and then wait.  
            string output = p.StandardOutput.ReadToEnd();
            p.WaitForExit();

            if (output.Contains("WARNING: Package(s) not found:"))
            {
                return false;
            }
            
            return true;
        }

        /***************************************************/
    }
}

