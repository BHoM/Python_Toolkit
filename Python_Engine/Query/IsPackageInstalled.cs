//
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
// 

using BH.oM.Python;
using BH.oM.Reflection.Attributes;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Query the given BHoM Python environment for existence of the given package.")]
        [Input("pythonEnvironment", "The BHoM Python environment.")]
        [Input("package", "The package to check the environment for.")]
        [Output("isInstalled", "True if package is installed.")]
        public static bool IsPackageInstalled(this PythonEnvironment pythonEnvironment, string package)
        {
            // get the installed packages
            Dictionary<string, string> installedPackages = new Dictionary<string, string>();
            foreach (string pkg in pythonEnvironment.InstalledPackages())
            {
                string[] pkgDetails = pkg.Split(new string[] { "==" }, System.StringSplitOptions.RemoveEmptyEntries);
                installedPackages.Add(pkgDetails.First(), pkgDetails.Last());
            }

            // determine the queried package (and version if it is included)
            string packageName = package.Split(new string[] { "==" }, System.StringSplitOptions.RemoveEmptyEntries).First();
            string packageVersion = null;
            if (package.Contains("=="))
            {
                packageVersion = package.Split(new string[] { "==" }, System.StringSplitOptions.RemoveEmptyEntries).Last();
            }

            // check for presence of package
            if (installedPackages.ContainsKey(packageName))
            {
                if (installedPackages[packageName] == packageVersion)
                {
                    return true;
                }
                else
                {
                    if (package.Contains("=="))
                    {
                        BH.Engine.Reflection.Compute.RecordError($"{package} is installed, but the current version does not match the requested version.");
                        return false;
                    }
                    else
                    {
                        BH.Engine.Reflection.Compute.RecordWarning($"{package} is installed, but requested package doesn't specify version.");
                    }
                }
                return true;
            }
            return false;
        }

        //        [Description("Return True if named Python package is installed in given environment.")]
        //        public static bool IsPackageInstalled(string package, string environmentName = null)
        //        {
        //            // get the associated executable with which to run Pip
        //            string environmentExecutable = Query.EmbeddedPythonExecutable();
        //            if (environmentName == null)
        //            {
        //                BH.Engine.Reflection.Compute.RecordNote("Checking for existence of {package} in the base BHoM Python environment.");
        //            }
        //            else
        //            {
        //                if (!environmentName.IsVirtualEnvironmentInstalled())
        //                {
        //                    return false;
        //                }
        //                environmentExecutable = environmentName.VirtualEnvironmentExecutable();
        //            }

        //            // run check
        //            string cmd = $"{environmentExecutable} -m pip show {package}";
        //            System.Diagnostics.Process p = new System.Diagnostics.Process();
        //            p.StartInfo.CreateNoWindow = true;
        //            p.StartInfo.WindowStyle = System.Diagnostics.ProcessWindowStyle.Hidden;
        //            p.StartInfo.UseShellExecute = false;
        //            p.StartInfo.RedirectStandardOutput = true;
        //            p.StartInfo.FileName = "cmd.exe";
        //            p.StartInfo.Arguments = $"/C {cmd}";
        //            p.Start();

        //            // To avoid deadlocks, always read the output stream first and then wait.  
        //            string output = p.StandardOutput.ReadToEnd();
        //            p.WaitForExit();

        //            if (output.Contains("WARNING: Package(s) not found:"))
        //            {
        //                return false;
        //            }

        //            return true;
        //        }

        /***************************************************/
    }
}
