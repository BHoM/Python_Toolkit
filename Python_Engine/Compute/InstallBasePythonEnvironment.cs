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
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install the base Python Environment for BHoM workflows.")]
        [Input("run", "Run the installation process for the BHoM Python Environment.")]
        [Output("env", "The base Python Environment for BHoM workflows.")]
        public static oM.Python.PythonEnvironment InstallBasePythonEnvironment(bool run = false)
        {
            if (!run)
            {
                BH.Engine.Base.Compute.RecordWarning($"Please toggle `{nameof(run)}` to true.");
                return null;
            }

            // Python version for base environment
            oM.Python.Enums.PythonVersion version = oM.Python.Enums.PythonVersion.v3_10_5;

            // set location where base Python env will be created
            string targetDirectory = Path.Combine(Query.EnvironmentsDirectory(), Query.ToolkitName());
            if (!Directory.Exists(targetDirectory))
                Directory.CreateDirectory(targetDirectory);

            // set executable path for later use in installation
            string executable = Path.Combine(targetDirectory, "python.exe");
            oM.Python.PythonEnvironment env = new oM.Python.PythonEnvironment() { Name = Query.ToolkitName(), Executable = executable };

            if (env.EnvironmentExists())
                return env;

            // create log of installation as process continues - useful for debugging if things go wrong!
            string logFile = Path.Combine(targetDirectory, "installation.log");

            // prepare constants for use in installation process
            string pythonUrl = version.EmbeddableURL();
            string pythonZipFile = Path.Combine(targetDirectory, "embeddable_python.zip");
            string pipInstallerUrl = "https://bootstrap.pypa.io/get-pip.py";
            string pipInstallerFile = Path.Combine(targetDirectory, "get-pip.py");

            using (StreamWriter sw = File.AppendText(logFile))
            {
                sw.WriteLine(LoggingHeader("Installation started for BHoM base Python environment"));

                // download and unpack files
                List<string> installationCommands = new List<string>() {
                    $"curl {pythonUrl} -o {pythonZipFile}", // download Python zip file
                    $"tar -v -xf {pythonZipFile} -C {targetDirectory}", // unzip files
                    $"del {pythonZipFile}", // remove zip file
                    $"curl {pipInstallerUrl} -o {pipInstallerFile}", // download PIP installer
                    $"{executable} {pipInstallerFile} --no-warn-script-location", // install PIP
                    $"del {pipInstallerFile}", // remove PIP installer file
                };

                foreach (string command in installationCommands)
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {command}");
                    sw.WriteLine(Compute.RunCommandStdout($"{command}", hideWindows: true));
                }

                // modify directory to replicate "normal" Python installation
                List<string> pthFiles = System.IO.Directory.GetFiles(targetDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith("._pth")).ToList();
                string libDirectory = System.IO.Directory.CreateDirectory(Path.Combine(targetDirectory, "DLLs")).FullName;
                List<string> libFiles = System.IO.Directory.GetFiles(targetDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => (s.EndsWith(".dll") || s.EndsWith(".pyd")) && !Path.GetFileName(s).Contains("python") && !Path.GetFileName(s).Contains("vcruntime")).ToList();

                List<string> modificationCommands = new List<string>() { };
                foreach (string pthFile in pthFiles)
                {
                    modificationCommands.Add($"del {pthFile}"); // delete *._pth file/s
                }
                foreach (string libFile in libFiles)
                {
                    modificationCommands.Add($"move /y {libFile} {libDirectory}"); // move specific *._pyd and *.dll file/s into DLLs directory
                }

                foreach (string command in modificationCommands)
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {command}");
                    sw.WriteLine(Compute.RunCommandStdout($"{command}", hideWindows: true));
                }

                // install packages into base environment
                string packageInstallationCommand = $"{executable} -m pip install --no-warn-script-location -e {Path.Combine(Query.CodeDirectory(), Query.ToolkitName())}";
                sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {packageInstallationCommand}");
                sw.WriteLine(Compute.RunCommandStdout($"{packageInstallationCommand}", hideWindows: true)); // install packages into this environment
                }

                return env;
        }
    }
}
