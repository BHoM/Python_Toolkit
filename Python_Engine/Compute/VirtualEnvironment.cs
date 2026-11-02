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
using System;
using System.ComponentModel;
using System.IO;
using System.Text.RegularExpressions;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Create a Python Virtual Environment of a given version and name.")]
        [Input("version", "The version of Python to use for this environment.")]
        [Input("name", "The name of this venv.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("venv", "The resultant venv.")]
        public static PythonEnvironment VirtualEnvironment(string version, string name, bool reload = true)
        {
            if (Query.VirtualEnvironmentExists(name))
            {
                if (reload)
                {
                    PythonEnvironment existingVenv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };
                    string existingVersion = Query.Version(existingVenv);
                    if (existingVersion == null || (existingVersion != version && !existingVersion.StartsWith(version + ".", StringComparison.Ordinal)))
                    {
                        BH.Engine.Base.Compute.RecordError($"The requested environment already exists using Python {existingVersion}, but is being requested with Python {version}. Either provide a different name, a matching version, or remove the existing environment.");
                        return null;
                    }
                    return existingVenv;
                }
                else
                {
                    RemoveVirtualEnvironment(name: name, run: true);
                }
            }

            InstallUV(true); // ensure UV is installed

            string directory = Path.Combine(Query.DirectoryEnvironments(), name);
            Directory.CreateDirectory(directory);

            string cmd = $"\"{Query.UVExecutable()}\" venv \"{Path.Combine(directory, ".venv")}\" --python \"{version}\"";
            if (RunCommandStdout(command: cmd, startDirectory: directory).Item3 != 0)
                return null;

            PythonEnvironment venv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };

            InstallJupyterKernel(venv: venv);

            return venv;
        }

        [Description("Create a Python Virtual Environment from a TOML file in the named BHoM environment directory. Before installation, set the project's version to the current BHoM version.")]
        [Input("tomlFile", "The path to a TOML file containing venv configuration.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("venv", "The resultant venv.")]
        public static PythonEnvironment VirtualEnvironment(string tomlFile, bool reload = true)
        {
            string name = Directory.GetParent(tomlFile).Name;
            string directory = Path.Combine(Query.DirectoryEnvironments(), name);

            // a package must have an associated TOML file, a README.md and a src/<package_name>
            if (!File.Exists(tomlFile))
            {
                Base.Compute.RecordError($"TOML file not found at {tomlFile}");
                return null;
            }

            string readmeFile = Path.Combine(directory, "README.md");
            if (!File.Exists(readmeFile))
            {
                Base.Compute.RecordError($"README.md file not found at {readmeFile}");
                return null;
            }

            string toml = File.ReadAllText(tomlFile);
            Match project = Regex.Match(toml, @"(?ms)^[ \t]*\[project\][ \t]*(?:#[^\r\n]*)?\r?\n(?<content>.*?)(?=^[ \t]*\[|\z)");
            string packageName = Regex.Match(project.Groups["content"].Value,
                @"(?m)^[ \t]*name[ \t]*=[ \t]*['""](?<name>[^'""\r\n]+)['""]").Groups["name"].Value;
            if (!project.Success || string.IsNullOrWhiteSpace(packageName))
            {
                Base.Compute.RecordError($"A [project] section with a package name is required in {tomlFile}.");
                return null;
            }

            string packageFile = Path.Combine(directory, "src", packageName, "__init__.py");
            if (!File.Exists(packageFile))
            {
                Base.Compute.RecordError($"A Python package must contain a .\\src\\{packageName}\\__init__.py file.");
                return null;
            }

            string projectContent = project.Groups["content"].Value;
            Regex versionField = new Regex(@"(?m)^(?<prefix>[ \t]*version[ \t]*=[ \t]*)(?<quote>['""])[^'""\r\n]*\k<quote>");
            if (!versionField.IsMatch(projectContent))
            {
                Base.Compute.RecordError($"A static [project] version is required in {tomlFile}.");
                return null;
            }

            if (Query.VirtualEnvironmentExists(name))
            {
                if (reload)
                {
                    PythonEnvironment existingVenv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };
                    return existingVenv;
                }
                else
                {
                    RemoveJupyterKernel(name, run: true);
                    // Retain the TOML file and package sources while recreating the environment.
                    Directory.Delete(Path.Combine(directory, ".venv"), true);
                }
            }

            string updatedProject = versionField.Replace(projectContent,
                match => match.Groups["prefix"].Value + $"\"{BH.Engine.Base.Query.BHoMVersion()}\"", 1);
            Group content = project.Groups["content"];
            File.WriteAllText(tomlFile, toml.Substring(0, content.Index) + updatedProject + toml.Substring(content.Index + content.Length));

            InstallUV(true); // ensure UV is installed

            string cmd = $"\"{Query.UVExecutable()}\" sync --all-packages";
            if (RunCommandStdout(cmd, startDirectory: directory).Item3 != 0)
                return null;

            PythonEnvironment venv = new PythonEnvironment() { Executable = Query.VirtualEnvironmentExecutable(name), Name = name };

            InstallJupyterKernel(venv: venv);

            return venv;
        }
    }
}
