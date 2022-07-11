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
        [Description("Uninstall packages by name from the executable associated with a Python environment.")]
        [Input("exe", "The path to a Python executable.")]
        [Input("packages", "A list of packages to uninstall.")]
        [Input("run", "A boolean flag to trigger package removal.")]
        [Output("result", "The output log of the uninstallation.")]
        public static string UninstallPackages(string exe, List<string> packages, bool run = false)
        {
            if (run)
            {
                string cmd = $"{Modify.AddQuotesIfRequired(exe)} -m pip uninstall -y {String.Join(" ", packages)}";
                return Compute.RunCommandStdout(cmd);
            }
            return null;
        }

        [Description("Uninstall packages by name from a BHoM Python environment.")]
        [Input("env", "A BHoM Python Environment object.")]
        [Input("packages", "A list of packages to uninstall.")]
        [Input("run", "A boolean flag to trigger package removal.")]
        [Output("result", "The output log of the uninstallation.")]
        public static string UninstallPackages(this oM.Python.PythonEnvironment env, List<string> packages, bool run = false)
        {
            return UninstallPackages(env.Executable, packages, run);
        }

        [Description("Uninstall a BHoM Python Environment.")]
        [Input("env", "A BHoM Python Environment object.")]
        [Input("run", "A boolean flag to trigger package removal.")]
        [Output("result", "The output log of the uninstallation.")]
        public static string UninstallPythonEnvironment(this oM.Python.PythonEnvironment env, bool run = false)
        {
            string log = "";
            if (run)
            {
                oM.Python.PythonEnvironment baseEnv = BH.Engine.Python.Compute.PythonToolkitEnvironment(true);

                if (env.Name != "Python_Toolkit")
                {
                    // remove ipykernel env for given env
                    string kernelRemoveCmd = $"{Modify.AddQuotesIfRequired(baseEnv.Executable)} -m jupyter kernelspec remove {env.Name}";
                    log += "\n" + Compute.RunCommandStdout(kernelRemoveCmd);
                }

                
                string envDir = Path.GetDirectoryName(env.Executable);
                if (envDir == Path.Combine(Query.EnvironmentsDirectory(), env.Name))
                {
                    // if env in Extensions, then remove env fully
                    DeleteDirectory(envDir);
                    return log;
                }
                else
                {
                    // if not in extensions, then remove reference to BHoM PythonCode
                    log += "\n" + env.UninstallPackages(new List<string>() { baseEnv.Name.ToLower().Replace("_", "-"), env.Name.ToLower().Replace("_", "-") });
                }
            }
            return log;
        }
    
    }
}
