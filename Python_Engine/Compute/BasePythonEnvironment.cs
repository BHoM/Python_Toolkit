/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2024, the respective contributors. All rights reserved.
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
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Retrieve or reinstall the base Python Environment for BHoM workflows.")]
        [Input("version", "The target version of python to be installed or retrieved.")]
        [Input("reload", "Reload the base Python environment rather than recreating it, if it already exists.")]
        [Input("run", "Start the installation/retrieval of the BHoM Base Python Environment.")]
        [Output("env", "The base Python Environment for all BHoM workflows.")]
        public static PythonEnvironment BasePythonEnvironment(
            PythonVersion version = PythonVersion.v3_10,
            bool reload = true,
            bool run = false
        )
        {
            if (!run)
            {
                return null;
            }

            if (!Directory.Exists(Query.DirectoryEnvironments()))
            {
                // create PythonEnvironments directory if it doesnt already exist
                Directory.CreateDirectory(Query.DirectoryEnvironments());
            }

            // determine whether the base environment already exists
            string targetExecutable = Path.Combine(Query.DirectoryBaseEnvironment(version), "python.exe");
            bool exists = File.Exists(targetExecutable);

            if (exists && reload)
                return new PythonEnvironment() { Name = Query.ToolkitName(), Executable = targetExecutable };

            if (exists && !reload)
                // remove all existing environments and kernels
                RemoveEverything();

            // download and run the installer for the target Python version
            string exe = version.DownloadPythonVersion();

            // install essential packages into base environment
            InstallPackages(exe, new List<string>() { "virtualenv", "jupyterlab", "black", "pylint" });

            InstallPackageLocal(Query.DirectoryCode(), Query.ToolkitName());

            return new PythonEnvironment() { Name = Query.ToolkitName(), Executable = exe };
        }
    }
}

