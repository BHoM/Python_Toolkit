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
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Using Pip, install a Python package/s.")]
        [Input("packages", "A list of packages to be installed, including version information (in the format \"<packageName>==<versionInfo>\".")]
        [Input("environmentName", "The name of the Python environment to which the packages should be installed. If left blank, this defaults to the base BHoM Python environment.")]
        [Input("force", "Set to True to force installation of this version, overwriting any existing package and version already installed.")]
        [Input("findLinks", "Set the location/s in which to look for certain packages.")]
        [Input("verbose", "Set to False to hide output.")]
        public static void PipInstall(List<string> packages, string environmentName = null, bool force = false, string findLinks = "", bool verbose = true)
        {
            if (packages == null || packages.Count == 0)
            {
                return;
            }

            // set the environment executable used to install the package/s
            string environmentExecutable;
            if (environmentName == null)
            {
                environmentExecutable = Query.EmbeddedPythonExecutable();
            }
            else
            {
                if (!environmentName.VirtualEnvironmentExists())
                {
                    return;
                }
                environmentExecutable = environmentName.VirtualEnvironmentExecutable();
            }

            string forceInstall = force ? "--force-reinstall" : "";

            if (findLinks != "" && !findLinks.StartsWith("-f "))
                findLinks = "-f " + findLinks;

            string verboseFlag = verbose ? "--verbose" : "";

            RunCommand($"{environmentExecutable} -m pip install {findLinks} {forceInstall} {verboseFlag} --no-warn-script-location {String.Join(" ", packages)}", hideWindows: true);
        }

        /***************************************************/
    }
}

