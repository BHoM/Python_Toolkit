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

using BH.oM.Python;
using BH.oM.Base.Attributes;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("List the available packages within the given BHoM Python environment.")]
        [Input("pythonEnvironment", "A BHoM Python environment.")]
        [Output("packages", "A list of installed packages.")]
        public static List<PythonPackage> InstalledPackages(this PythonEnvironment pythonEnvironment)
        {
            string tempPackageFile = Path.Combine(Path.GetTempPath(), "packages.txt");
            string command = $"{pythonEnvironment.PythonExecutable()} -m pip freeze > {tempPackageFile}";
            
            Compute.RunCommandBool(command, hideWindows: true);

            List<string> installedPackages = new List<string>(File.ReadAllLines(tempPackageFile));
            File.Delete(tempPackageFile);

            List<PythonPackage> packages = new List<PythonPackage>();
            foreach (string pkgString in installedPackages)
            {
                string[] parts = pkgString.Split(new string[] { "==" }, StringSplitOptions.None);

                packages.Add(
                    new PythonPackage()
                    {
                        Name = parts.First(),
                        Version = parts.Last(),
                    }
                );
            }

            return packages;
        }

        /***************************************************/
    }
}


