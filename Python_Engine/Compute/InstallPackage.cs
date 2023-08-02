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
using BH.oM.Python;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using System.Xml.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install a list of packages to a given Python executable.")]
        [Input("executable", "The Python executable to install the packages to.")]
        [Input("packages", "The packages to install.")]
        public static void InstallPackages(
            string executable,
            List<string> packages
        )
        {
            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError("Python executable not found at " + executable);
            }

            if (packages.Count == 0)
            {
                BH.Engine.Base.Compute.RecordError("No packages to install.");
            }

            System.Diagnostics.Process process = new System.Diagnostics.Process()
            {
                StartInfo = new System.Diagnostics.ProcessStartInfo()
                {
                    FileName = executable,
                    Arguments = "-m pip install --no-warn-script-location " + string.Join(" ", packages),
                    UseShellExecute = false,
                    RedirectStandardError = true,
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error installing packages [{string.Join(" ", packages)}].\n{p.StandardError.ToString()}");
            }
        }

        [Description("Install a list of packages to a given Python executable.")]
        [Input("environment", "The Python environment to install the packages to.")]
        [Input("packages", "The packages to install.")]
        public static void InstallPackages(
            this PythonEnvironment environment,
            List<string> packages
        )
        {
            InstallPackages(environment.Executable, packages);
        }

        [Description("Install packages from a requirements.txt file to a given Python executable.")]
        [Input("executable", "The Python executable to install the packages to.")]
        [Input("requirements", "The requirements.txt file to install.")]
        public static void InstallRequirements(
            string executable,
            string requirements
        )
        {
            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError("Python executable not found at " + executable);
            }

            if (!File.Exists(requirements))
            {
                BH.Engine.Base.Compute.RecordError("requirements.txt not found at " + requirements);
            }

            
            System.Diagnostics.Process process = new System.Diagnostics.Process()
            {
                StartInfo = new System.Diagnostics.ProcessStartInfo()
                {
                    FileName = executable,
                    Arguments = "-m pip install --no-warn-script-location -r " + requirements,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error installing packages from {requirements}.\n{p.StandardError.ToString()}");
            }
        }

        [Description("Install packages from a requirements.txt file to a given Python environment.")]
        [Input("environment", "The Python environment to install the packages to.")]
        [Input("requirements", "The requirements.txt file to install.")]
        public static void InstallRequirements(
            this PythonEnvironment environment,
            string requirements
        )
        {
            InstallRequirements(environment.Executable, requirements);
        }


        [Description("Install a local Python package to a given Python executable.")]
        [Input("executable", "The Python executable to install the package to.")]
        [Input("packageDirectory", "The package to install.")]
        public static void InstallPackageLocal(
            string executable,
            string packageDirectory
        )
        {
            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError("Python executable not found at " + executable);
            }

            string pip = Path.Combine(Path.GetDirectoryName(executable), "Scripts", "pip.exe");
            if (!File.Exists(pip))
            {
                BH.Engine.Base.Compute.RecordError("pip not found at " + pip);
            }

            System.Diagnostics.Process process = new System.Diagnostics.Process()
            {
                StartInfo = new System.Diagnostics.ProcessStartInfo()
                {
                    FileName = pip,
                    Arguments = $"install --no-warn-script-location -e \"{packageDirectory}\"",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error installing package from \"{packageDirectory}\".\n{p.StandardError.ToString()}");
            }
        }

        [Description("Install a local Python package to a given Python environment.")]
        [Input("environment", "The Python environment to install the packages to.")]
        [Input("packageDirectory", "The package to install.")]
        public static void InstallPackageLocal(
            this PythonEnvironment environment,
            string packageDirectory
        )
        {
            InstallPackageLocal(environment.Executable, packageDirectory);
        }
    }
}
