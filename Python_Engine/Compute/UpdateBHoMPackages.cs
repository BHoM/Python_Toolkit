/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
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

using BH.oM.Base.Attributes;
using BH.oM.Python;
using BH.oM.Python.Enums;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Text;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Using the environment name (and version if the environment name is the base python environment), directly install/update missing BHoM packages.")]
        [Input("environmentName", "The name of the environment to update.")]
        [Input("version", "If the environment name is the name of the base python environment, the version that needs updating.")]
        public static void UpdateBHoMPackages(this string environmentName, PythonVersion version = PythonVersion.Undefined)
        {
            //construct the expected PythonEnvironment and pass to UpdateBHoMPackages
            PythonEnvironment env = new PythonEnvironment()
            {
                Name = environmentName,
            };

            //python version is only used if the environment name is this toolkits name.
            if (environmentName == Query.ToolkitName())
            {
                if (version == PythonVersion.Undefined)
                {
                    BH.Engine.Base.Compute.RecordError("The version must be specified when updating BHoM packages for a base python environment. No updates have occurred.");
                    return;
                }

                env.Executable = Path.Combine(Query.DirectoryBaseEnvironment(version), "python.exe");
            }
            else
                env.Executable = Query.VirtualEnvironmentExecutable(environmentName);

            UpdateBHoMPackages(env);
        }

        /***************************************************/

        [Description("Using a PythonEnvironment, directly install/update missing BHoM packages.")]
        [Input("environment", "The python environment to update.")]
        public static void UpdateBHoMPackages(this PythonEnvironment environment)
        {
            if (!File.Exists(environment.Executable))
            {
                BH.Engine.Base.Compute.RecordError($"Given environment or base install {environment.Executable} does not exist.");
                return;
            }

            string localPackageDirectory = ResolvePackageDirectory(environment);

            if (!Directory.Exists(localPackageDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"There is no local package directory for {environment.Name} (searched at \"{localPackageDirectory}\"). No packages were updated.");
                return;
            }

            InstallPackageLocal(environment, localPackageDirectory);
        }

        /***************************************************/

        private static string ResolvePackageDirectory(PythonEnvironment environment)
        {
            string packageName = environment.Name;
            string codeDirectory = Query.DirectoryCode();
            return Path.Combine(codeDirectory, packageName);
        }
    }
}