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

using System.Collections.Generic;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static void PipInstall(string module_name, string version = "", bool force = false, string findLinks = "", bool verbose = true)
        {
            if (Query.IsModuleInstalled(module_name) && !force)
                return;

            string pipPath = Path.Combine(Query.EmbeddedPythonHome(), "Scripts", "pip3");
            string forceInstall = force ? "--force-reinstall" : "";
            if (version.Length > 0)
                version = $"=={version}";

            if (findLinks != "")
                findLinks = "-f " + findLinks;

            string verboseFlag = verbose ? "--verbose" : "";

            RunCommand($"{pipPath} install {module_name}{version} {findLinks} {forceInstall} {verboseFlag} --no-warn-script-location");
        }

        public static void PipInstall(string pythonExecutable, List<string> packages, bool force = false, string findLinks = "", bool verbose = true)
        {
            if (packages == null || packages.Count == 0)
            {
                return;
            }

            string forceInstall = force ? "--force-reinstall" : "";

            if (findLinks != "")
                findLinks = "-f " + findLinks;

            string verboseFlag = verbose ? "--verbose" : "";

            string cmd = "";
            foreach (string package in packages)
            {
                cmd += $" {package}";
            }

            RunCommand($"{pythonExecutable} -m pip install {findLinks} {forceInstall} {verboseFlag} --no-warn-script-location {cmd}");
        }

        /***************************************************/
    }
}

