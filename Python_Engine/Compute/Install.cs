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

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install UV, the Python manager used in these tools, and the ruff, jupyterlab and sphinx tools.")]
        [Input("run", "Set to True to install UV and its core tools.")]
        public static void InstallUV(bool run = false)
        {
            if (!run)
                return;

            try
            {
                string uvBinPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".local", "bin");
                if (Directory.Exists(uvBinPath))
                    Environment.SetEnvironmentVariable("PATH", uvBinPath + Path.PathSeparator + Environment.GetEnvironmentVariable("PATH"));

                int exitCode;
                string location = RunCommandStdout("where.exe uv.exe", out exitCode);
                if (exitCode != 0)
                {
                    Base.Compute.RecordNote("Installing UV.");
                    string output = RunCommandStdout(
                        "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command \"$ErrorActionPreference = 'Stop'; irm https://astral.sh/uv/install.ps1 | iex\"",
                        out exitCode);
                    if (exitCode != 0)
                    {
                        Base.Compute.RecordError(exception: new Exception(), message: $"Failed to install UV (exit code {exitCode}).\n{output}");
                        return;
                    }

                    // The installer cannot update the environment of this already-running process.
                    if (Directory.Exists(uvBinPath))
                        Environment.SetEnvironmentVariable("PATH", uvBinPath + Path.PathSeparator + Environment.GetEnvironmentVariable("PATH"));

                    location = RunCommandStdout("where.exe uv.exe", out exitCode);
                }

                if (exitCode != 0)
                {
                    Base.Compute.RecordError(exception: new Exception(), message: $"Could not locate UV on PATH after installation.\n{location}");
                    return;
                }

                string uvExecutable = location.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries)[0];

                foreach (string tool in new[] { "ruff", "jupyterlab", "sphinx" })
                {
                    string output = RunCommandStdout($"\"\"{uvExecutable}\" tool install {tool}\"", out exitCode);
                    if (exitCode != 0)
                    {
                        Base.Compute.RecordError(exception: new Exception(), message: $"Failed to install {tool} to UV (exit code {exitCode}).\n{output}");
                    }
                }
            }
            catch (System.ComponentModel.Win32Exception ex)
            {
                Base.Compute.RecordError(exception: new Exception(), message: $"Could not run the UV installation command. {ex.Message}");
            }
            catch (TimeoutException ex)
            {
                Base.Compute.RecordError(exception: new Exception(), message: $"UV installation timed out. {ex.Message}");
            }
        }

        [Description("Register a Jupyer kernel for a given venv.")]
        [Input("venv", "The Python environment to install the packages to.")]
        public static void InstallJupyterKernel(PythonEnvironment venv)
        {
            string cmd = $"{venv.Executable} -m ipykernel insatll --user --name {venv.Name} --display-name {venv.Name}";
            RunCommandStdout(command: cmd, hideWindows: true);
        }

        [Description("Install a list of packages to a given Python executable.")]
        [Input("venv", "The Python environment to install the packages to.")]
        [Input("packages", "The packages to install.")]
        [Input("run", "Run this method.")]
        public static void InstallPackages(
            this PythonEnvironment venv,
            List<string> packages,
            bool run = false
        )
        {
            string cmd = $"uv add {string.Join(" ", packages)}";
            string directory = Query.VirtualEnvironmentDirectory(venv.Name);

            if (run)
            { 
                string result = RunCommandStdout(cmd, out int exitCode, startDirectory: directory);
            }
            else
            {
                Base.Compute.RecordNote($"The following command will be executed from \"{directory}\": {cmd}");
            }
        }

        [Description("Install a local Python package to a given Python environment.")]
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
                Base.Compute.RecordError($"{packageDirectory} not found.");

            string cmd = $"uv add --editable {packageDirectory}";
            string directory = Query.VirtualEnvironmentDirectory(venv.Name);

            if (run)
            {
                string result = RunCommandStdout(cmd, out int exitCode, startDirectory: directory);
            }
            else {
                Base.Compute.RecordNote($"The following command will be executed from \"{directory}\": {cmd}");
            }
        }
    }
}
