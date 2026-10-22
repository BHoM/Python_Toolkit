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
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Create a Python Virtual Environment of a given version and name.")]
        [Input("version", "The version of Python to use for this environment.")]
        [Input("name", "The name of this venv.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("venv", "The executable for the resultant venv.")]
        public static PythonEnvironment VirtualEnvironment(string version, string name, bool reload = true)
        {
            if (Query.VirtualEnvironmentExists(name))
            {
                if (reload)
                {
                    return new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };
                }
                else
                {
                    RemoveVirtualEnvironment(name: name, run: true);
                    RemoveKernel(name: name, run: true);
                }
            }

            InstallUV(true); // ensure UV is installed

            string directory = Path.Combine(Query.DirectoryEnvironments(), name);
            string cmd = $"uv venv {Path.Combine(directory, "venv")} --python {version}";
            RunCommandStdout(cmd, out int exitCode, startDirectory: directory);

            PythonEnvironment venv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };

            InstallJupyterKernel(venv: venv);

            return venv;
        }

        [Description("Create a Python Virtual Environment from a TOML file. This will create the venv alongside that TOML file.")]
        [Input("tomlFile", "The path to a TOML file containing venv configuration.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("venv", "The executable for the resultant venv.")]
        public static PythonEnvironment VirtualEnvironment(string tomlFile, bool reload = true)
        {
            if (!File.Exists(tomlFile))
            {
                Base.Compute.RecordError($"TOML file not found at {tomlFile}");
                return null;
            }

            string name = Directory.GetParent(tomlFile).Name;
            if (Query.VirtualEnvironmentExists(name))
            {
                if (reload)
                {
                    return new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };
                }
                else
                {
                    RemoveVirtualEnvironment(name);
                    RemoveKernel(name);
                }
            }

            InstallUV(true); // ensure UV is installed

            string directory = Path.Combine(Query.DirectoryEnvironments(), name);
            string cmd = "uv sync --all-packages";
            RunCommandStdout(cmd, out int exitCode, startDirectory: directory);

            PythonEnvironment venv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };

            InstallJupyterKernel(venv: venv);

            return venv;
        }
    }
}
