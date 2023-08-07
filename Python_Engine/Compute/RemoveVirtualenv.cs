/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2023, the respective contributors. All rights reserved.
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
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        // TODO - REMOVE THIS METHOD, NO LONGER REQUIRED
        [Description("Remove a virtualenv of the given name.")]
        [Input("name", "The name of this virtualenv to remove.")]
        [Input("run", "Run the installation process for this virtualenv.")]
        [Output("success", "True if the environment of the given name has been removed.")]
        public static bool RemoveVirtualenv(
            string name,
            bool run = false
        )
        {
            if (run)
            {
                string bhomPythonExecutable = Path.Combine(Query.EnvironmentsDirectory(), Query.ToolkitName(), "python.exe");

                string targetDirectory = Path.Combine(Query.EnvironmentsDirectory(), name);
                oM.Python.PythonEnvironment env = new oM.Python.PythonEnvironment() { Name = name, Executable = Path.Combine(targetDirectory, "Scripts", "python.exe") };

                if (env.EnvironmentExists())
                {
                    string logFile = Path.Combine(Query.EnvironmentsDirectory(), "removal.log");

                    List<string> uninstallationCommands = new List<string>() {
                        $"rmdir {Modify.AddQuotesIfRequired(targetDirectory)} /S /Q",  // delete folder and contents of given env name
                        $"{bhomPythonExecutable} -m jupyter kernelspec remove {name.ToLower()} -y",  // remove the registered kernel
                    };
                    using (StreamWriter sw = File.AppendText(logFile))
                    {
                        sw.WriteLine(LoggingHeader($"Uninstalling {name} BHoM Python environment"));

                        foreach (string command in uninstallationCommands)
                        {
                            sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {command}");
                            Compute.RunCommandStdout($"{command}", hideWindows: true);
                        }
                    }
                    return true;
                }
                else
                {
                    BH.Engine.Base.Compute.RecordError($"{Query.ToString(env)} wasn't found and can not be removed.");
                }
            }
            return false;
        }
    }
}

