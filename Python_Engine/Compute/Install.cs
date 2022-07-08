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
        [Description("Install Python of the given version into a target directory.")]
        [Input("version", "The version of Python to install.")]
        [Input("name", "The name for this Python Environment.")]
        [Input("additionalPackages", "A list of directories containing additional local Python packages to be installed into this environment.")]
        [Input("directory", "The directory into which Python will be installed. By default, this value is C:/ProgramData/BHoM/Extensions/PythonEnvironments.")]
        [Output("env", "The installed BHoM Python environment.")]
        public static oM.Python.PythonEnvironment InstallPythonEnvironment(oM.Python.Enums.PythonVersion version, string name, List<string> additionalPackages = null, string directory = null)
        {
            if (directory == null)
                directory = "C:/ProgramData/BHoM/Extensions/PythonEnvironments";

            string targetDirectory = Path.Combine(directory, name);

            if (!Query.ValidEnvironmentName(name))
            {
                BH.Engine.Base.Compute.RecordError("Invalid BHoM PythonEnvironment name. \"name\" should contain no special characters or spaces.");
                return null;
            }

            if (Query.EnvironmentExists(directory, name))
            {
                BH.Engine.Base.Compute.RecordError($"A Python Environment named {targetDirectory} already exists.");
                return null;
            }

            // create the directory in which Python will be installed
            if (!Directory.Exists(targetDirectory))
                Directory.CreateDirectory(targetDirectory);

            // download the target version of Python
            string embeddablePythonZip = Compute.DownloadFile(version.EmbeddableURL());

            // extract embeddable python into environment directory
            System.IO.Compression.ZipFile.ExtractToDirectory(embeddablePythonZip, targetDirectory);

            // run the pip installer
            string executable = Path.Combine(targetDirectory, "python.exe");
            string pipInstallerPy = Compute.DownloadFile("https://bootstrap.pypa.io/get-pip.py");
            string installPipCommand = $"{executable} {pipInstallerPy} && exit";
            if (!Compute.RunCommandBool(installPipCommand, hideWindows: true))
            {
                BH.Engine.Base.Compute.RecordError($"Pip installation did not work using the command {installPipCommand}.");
                return null;
            }

            // remove _pth file
            List<string> pthFiles = System.IO.Directory.GetFiles(targetDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith("._pth")).ToList();
            foreach (string pthFile in pthFiles)
            {
                try
                {
                    File.Delete(pthFile);
                }
                catch (Exception e)
                {
                    BH.Engine.Base.Compute.RecordError($"{pthFile} not found to be deleted: {e}.");
                    return null;
                }
            }

            // move PYD and DLL files to DLLs directory
            string libDirectory = System.IO.Directory.CreateDirectory(Path.Combine(targetDirectory, "DLLs")).FullName;
            List<string> libFiles = System.IO.Directory.GetFiles(targetDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => (s.EndsWith(".dll") || s.EndsWith(".pyd")) && !Path.GetFileName(s).Contains("python") && !Path.GetFileName(s).Contains("vcruntime")).ToList();
            foreach (string libFile in libFiles)
            {
                string newLibFile = Path.Combine(libDirectory, Path.GetFileName(libFile));
                try
                {
                    File.Move(libFile, newLibFile);
                }
                catch (Exception e)
                {
                    BH.Engine.Base.Compute.RecordError($"{libFile} not capable of being moved to {newLibFile}: {e}.");
                    return null;
                }
            }

            // install additional Python code
            if (additionalPackages != null)
            {
                foreach (string pkg in additionalPackages)
                {
                    Compute.InstallLocalPackage(executable, pkg);
                }
            }

            // install ipykernel and register environment with the base BHoM Python environment
            Compute.InstallPackages(executable, new List<string>() { "ipykernel" });
            string kernelCreateCmd = $"{Modify.AddQuotesIfRequired(executable)} -m ipykernel install --name={name}";
            string kernelRegistry = Compute.RunCommandStdout(kernelCreateCmd);

            return new oM.Python.PythonEnvironment() { Name = name, Executable = executable };
        }

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
