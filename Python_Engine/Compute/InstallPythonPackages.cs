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

using BH.oM.Python;
using BH.oM.Reflection.Attributes;

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install packages into an existing BHoM Python environment.")]
        [Input("pythonEnvironment", "A BHoM Python environment.")]
        [Input("packages", "A list of BHoM PythonPackages.")]
        [Input("force", "Set to the Pip install --force flag to True to force installation of the given PythonPackages.")]
        [Input("run", "Set to True to install the PythonPackages.")]
        [Output("pythonEnvironment", "The BHoM PythonEnvironment object, now with more packages!")]
        public static PythonEnvironment InstallPythonPackages(this PythonEnvironment pythonEnvironment, List<PythonPackage> packages, bool force = false, bool run = false)
        {
            if (run)
            {
                if (Query.LoadPythonEnvironment(pythonEnvironment.Name) == null)
                {
                    BH.Engine.Reflection.Compute.RecordError("The environment given doesn't exist.");
                    return null;
                }

                List<string> packagesStrings = new List<string>();
                foreach (PythonPackage package in packages)
                {
                    packagesStrings.Add(package.GetString());
                }
                if (packagesStrings.Count() > 0)
                {
                    string command = $"{Query.PythonExecutable(pythonEnvironment)} -m pip install --no-warn-script-location{(force ? " --force-reinstall" : "")} {String.Join(" ", packagesStrings)} > {Path.Combine(pythonEnvironment.EnvironmentDirectory(), "package_install.log")} && exit";
                    if (!Compute.RunCommandBool(command, hideWindows: true))
                    {
                        BH.Engine.Reflection.Compute.RecordError($"Packages not installed for some reason.");
                        return null;
                    }
                }
                return pythonEnvironment;
            }
            else
            {
                return null;
            }
        }
    }
}
