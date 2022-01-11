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

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Query for the existence of a BHoM Python environment.")]
        [Input("pythonEnvironment", "The PythonEnvironment to check for.")]
        [Output("isInstalled", "True if environment is installed.")]
        public static bool IsInstalled(this PythonEnvironment pythonEnvironment)
        {
            if (!Directory.Exists(Path.Combine(Query.EnvironmentsDirectory(), pythonEnvironment.Name)) && !File.Exists(Path.Combine(Query.EnvironmentsDirectory(), pythonEnvironment.Name, "python.exe")))
            {
                return false;
            }
            return true;
        }

        [Description("Query for the existence of a package in a given BHoM Python environment.")]
        [Input("pythonEnvironment", "The PythonEnvironment to check for a specific PythonPackage.")]
        [Input("package", "A BHoM PythonPackage object.")]
        [Output("isInstalled", "True if package is installed.")]
        public static bool IsInstalled(this PythonEnvironment pythonEnvironment, PythonPackage package)
        {
            List<PythonPackage> packages = pythonEnvironment.InstalledPackages();
            if (packages.PackageInList(package))
            {
                return true;
            }
            return false;
        }

        /***************************************************/

        public static bool IsPythonInstalled()
        {
            return File.Exists(Path.Combine(Query.EmbeddedPythonHome(), "python.exe"));

        }

        /***************************************************/

        public static bool IsPipInstalled()
        {
            return File.Exists(Path.Combine(Query.EmbeddedPythonHome(), "Scripts", "pip.exe"));
        }

        /***************************************************/

        public static bool IsModuleInstalled(string module)
        {
            if (!IsPythonInstalled())
                return false;

            module = module.Split('.')[0];

            string packagesDir = Path.Combine(Query.EmbeddedPythonHome(), "Lib", "site-packages");
            string moduleDir = Path.Combine(packagesDir, module);
            bool installed = Directory.Exists(moduleDir) && File.Exists(Path.Combine(moduleDir, "__init__.py"));
            installed |= File.Exists(Path.Combine(packagesDir, module.Split('_')[0] + "-Toolkit.egg-link"));
            return installed;
        }

        /***************************************************/
    }
}

