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
        [Description("Install a list of Python packages into the Python environment associated with the given executable.")]
        [Input("exe", "The path to a Python executable.")]
        [Input("packages", "A list of Python packages.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given packages.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallPackages(string exe, List<string> packages, bool force = false)
        {
            string command = $"{Modify.AddQuotesIfRequired(exe)} -m pip install --no-warn-script-location{(force ? " --force-reinstall" : "")} {String.Join(" ", packages)}";
            return Compute.RunCommandStdout(command);
        }

        [Description("Install Python packages into the Python environment associated with the given executable, using a requirements.txt file.")]
        [Input("exe", "The path to a Python executable.")]
        [Input("requirements", "The path to a requirements.txt file.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given packages.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallPackages(string exe, string requirements, bool force = false)
        {
            string command = $"{Modify.AddQuotesIfRequired(exe)} -m pip install --no-warn-script-location{(force ? " --force-reinstall" : "")} -r {Modify.AddQuotesIfRequired(requirements)}";
            return Compute.RunCommandStdout(command);
        }

        [Description("Install packages into a BHoM Python environment.")]
        [Input("env", "The BHoM Python environment.")]
        [Input("packages", "A list of Python packages.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given packages.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallPackages(this PythonEnvironment env, List<string> packages, bool force = false)
        {
            return InstallPackages(env.Executable, packages, force);
        }

        [Description("Install packages into a BHoM Python environment.")]
        [Input("env", "The BHoM Python environment.")]
        [Input("requirements", "The path to a requirements.txt file.")]
        [Input("force", "Set the Pip install --force flag to True, to force installation of the given packages.")]
        [Output("result", "The output log of the package install process.")]
        public static string InstallPackages(this PythonEnvironment env, string requirements, bool force = false)
        {
            return InstallPackages(env.Executable, requirements, force);
        }
    }
}

