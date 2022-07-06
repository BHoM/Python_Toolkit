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

using BH.oM.Base.Attributes;
using BH.oM.Python;
using BH.oM.Python.Enums;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install a local Python packages into a Python environment associated with the given executable.")]
        [Input("exe", "The path to a Python executable.")]
        [Input("packageDirectory", "A directory containing a Python package.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given package.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallLocalPackage(string exe, string packageDirectory, bool force = false)
        {
            string cmd = $"{Modify.AddQuotesIfRequired(exe)} -m pip install --no-warn-script-location{(force ? " --force-reinstall" : "")} -e {Modify.AddQuotesIfRequired(packageDirectory)}";
            return Compute.RunCommandStdout(cmd);
        }

        [Description("Install a local Python packages into a BHoM Python environment.")]
        [Input("env", "The BHoM Python environment.")]
        [Input("packageDirectory", "A directory containing a Python package.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given packages.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallLocalPackage(this PythonEnvironment env, string packageDirectory, bool force = false)
        {
            return InstallLocalPackage(env.Executable, packageDirectory, force);
        }
    }
}

