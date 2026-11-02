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
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install UV in the BHoM tools directory and add that directory to the process PATH. Install any missing ruff, jupyterlab and sphinx tools; UV installations elsewhere are not used.")]
        [Input("run", "Set to True to install UV and its core tools.")]
        public static void InstallUV(bool run = false)
        {
            if (!run)
                return;

            string toolsDirectory = Query.DirectoryTools();

            string uvExecutable = Query.UVExecutable();
            if (!File.Exists(uvExecutable))
            {
                var installation = RunCommandStdout(
                    command: $"powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command \"$ErrorActionPreference = 'Stop'; $env:UV_INSTALL_DIR = '{toolsDirectory.Replace("'", "''")}'; $env:UV_NO_MODIFY_PATH = '1'; irm https://astral.sh/uv/install.ps1 | iex\"");
                if (installation.Item3 != 0)
                    return;
                if (!File.Exists(uvExecutable))
                {
                    Base.Compute.RecordError($"UV installation did not produce an executable at {uvExecutable}.");
                    return;
                }
            }

            string[] otherPaths = (Environment.GetEnvironmentVariable("PATH") ?? string.Empty).Split(Path.PathSeparator)
                .Where(directory => !string.Equals(directory.Trim().Trim('"'), toolsDirectory, StringComparison.OrdinalIgnoreCase))
                .ToArray();
            Environment.SetEnvironmentVariable("PATH", string.Join(Path.PathSeparator.ToString(), new[] { toolsDirectory }.Concat(otherPaths)));

            var installedTools = RunCommandStdout($"\"{uvExecutable}\" tool list");
            if (installedTools.Item3 != 0)
                return;

            var installedNames = new HashSet<string>(
                installedTools.Item1.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                    .Where(line => !line.StartsWith("-"))
                    .Select(line => line.Split(' ')[0]), StringComparer.OrdinalIgnoreCase);
            foreach (string tool in new[] { "ruff", "jupyterlab", "sphinx" })
            {
                if (!installedNames.Contains(tool))
                    RunCommandStdout($"\"{uvExecutable}\" tool install {tool}");
            }
        }

        [Description("Register a Jupyter kernel for a given venv unless that kernel already exists.")]
        [Input("venv", "The Python environment to install the packages to.")]
        public static void InstallJupyterKernel(this PythonEnvironment venv)
        {
            if (JupyterKernelExists(venv, venv.Name, true) != false)
                return;

            venv.InstallPackages(packages: new List<string>() { "ipykernel" }, true);
            string directory = Query.VirtualEnvironmentDirectory(venv.Name);

            string cmd = $"\"{venv.Executable}\" -m ipykernel install --user --name \"{venv.Name}\" --display-name \"{venv.Name}\"";
            RunCommandStdout(command: cmd, startDirectory: directory);
        }

        [PreviousVersion("9.3", "BH.Engine.Python.Compute.InstallPackages(PythonEnvironment, List<string>)")]
        [Description("Install a list of packages to a given Python executable. UV retains satisfied versions and registers project dependencies when applicable.")]
        [Input("venv", "The Python environment to install the packages to.")]
        [Input("packages", "The packages to install.")]
        [Input("run", "Run this method.")]
        public static void InstallPackages(
            this PythonEnvironment venv,
            List<string> packages,
            bool run = false
        )
        {
            string directory = Query.VirtualEnvironmentDirectory(venv.Name);
            bool isProject = File.Exists(Path.Combine(directory, "pyproject.toml"));

            string uvCommand = isProject ? "add" : "pip install";
            string cmd = $"\"{Query.UVExecutable()}\" {uvCommand} --python \"{venv.Executable}\" {string.Join(" ", packages.Select(package => $"\"{package}\""))}";

            if (run)
            {
                RunCommandStdout(command: cmd, startDirectory: directory);
            }
            else
            {
                Base.Compute.RecordNote($"The following command will be executed from \"{directory}\": {cmd}");
            }
        }

        [PreviousVersion("9.3", "BH.Engine.Python.Compute.InstallPackages(PythonEnvironment, string)")]
        [Description("Install a local editable Python package. An unchanged installation from the same directory is retained; project dependencies are still registered.")]
        [Input("venv", "The Python environment to install the packages to.")]
        [Input("packageDirectory", "The package to install.")]
        [Input("run", "Run this method.")]
        public static void InstallPackageLocal(
            this PythonEnvironment venv,
            string packageDirectory,
            bool run = false
        )
        {
            if (!Directory.Exists(packageDirectory))
            {
                Base.Compute.RecordError($"{packageDirectory} not found.");
                return;
            }

            packageDirectory = Path.GetFullPath(packageDirectory);
            string directory = Query.VirtualEnvironmentDirectory(venv.Name);
            bool isProject = File.Exists(Path.Combine(directory, "pyproject.toml"));

            string uvCommand = isProject ? "add" : "pip install";
            string cmd = $"\"{Query.UVExecutable()}\" {uvCommand} --python \"{venv.Executable}\" --editable \"{packageDirectory}\"";

            if (run)
            {
                if (!isProject)
                {
                    // Explicit local paths are otherwise always reinstalled by UV.
                    string script = "import importlib.metadata as m,json,pathlib,sys; "
                        + "p=pathlib.Path(sys.argv[1]).resolve(); "
                        + "sources=[p/f for f in ('pyproject.toml','setup.py','setup.cfg') if (p/f).exists()]; "
                        + "print(any((lambda u: u.get('dir_info',{}).get('editable',False) and "
                        + "u.get('url','').rstrip('/').lower()==p.as_uri().rstrip('/').lower() and "
                        + "all(f.stat().st_mtime<=pathlib.Path(d.locate_file(x)).stat().st_mtime for f in sources))"
                        + "(json.loads(d.read_text('direct_url.json') or '{}')) "
                        + "for d in m.distributions() for x in (d.files or []) if str(x).endswith('.dist-info/METADATA')))";
                    var installed = RunCommandStdout(
                        $"\"{venv.Executable}\" -c \"{script}\" \"{packageDirectory}\"", startDirectory: directory);
                    if (installed.Item3 != 0)
                        return;
                    if (installed.Item1 == "True")
                        return;
                    if (installed.Item1 != "False")
                    {
                        Base.Compute.RecordError($"Could not check the local package installation in {venv.Name}.");
                        return;
                    }
                }
                RunCommandStdout(command: cmd, startDirectory: directory);
            }
            else
            {
                Base.Compute.RecordNote($"The following command will be executed from \"{directory}\": {cmd}");
            }
        }

        private static bool? JupyterKernelExists(PythonEnvironment venv, string name, bool requireMatchingExecutable = false)
        {
            string script = "import importlib.util,pathlib,sys; "
                + "available=importlib.util.find_spec('jupyter_client') is not None; "
                + "manager=__import__('jupyter_client.kernelspec',fromlist=['KernelSpecManager']).KernelSpecManager() if available else None; "
                + "exists=available and sys.argv[1].lower() in manager.find_kernel_specs(); "
                + "print(exists and (sys.argv[2]=='False' or "
                + "pathlib.Path(manager.get_kernel_spec(sys.argv[1].lower()).argv[0]).resolve()==pathlib.Path(sys.executable).resolve()))";
            var result = RunCommandStdout($"\"{venv.Executable}\" -c \"{script}\" \"{name}\" {requireMatchingExecutable}");
            if (result.Item3 != 0)
                return null;
            if (result.Item1 == "True")
                return true;
            if (result.Item1 == "False")
                return false;

            Base.Compute.RecordError($"Could not check whether Jupyter kernel {name} exists.");
            return null;
        }

        [Description("Install the Python_Toolkit Python venv.")]
        [Input("run", "Run this method.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("venv", "The resultant venv.")]
        public static PythonEnvironment InstallPythonToolkitVenv(
            bool run = false,
            bool reload = true
        )
        {
            string tomlFile = Path.Combine(Query.DirectoryEnvironments(), Query.ToolkitName(), "pyproject.toml");
            if (run)
            {
                return VirtualEnvironment(tomlFile: tomlFile, reload: reload);
            }
            return null;
        }
    }
}
