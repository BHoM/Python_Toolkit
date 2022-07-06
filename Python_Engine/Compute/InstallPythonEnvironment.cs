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
        [Input("additionalPackage", "A directory containing an additional Python package to be installed into this environment.")]
        [Input("directory", "The directory into which Python will be installed. By default, this value is C:/ProgramData/BHoM/Extensions/PythonEnvironments.")]
        [Output("env", "The installed BHoM Python environment.")]
        public static oM.Python.PythonEnvironment InstallPythonEnvironment(oM.Python.Enums.PythonVersion version, string name, string additionalPackage = null, string directory = "C:/ProgramData/BHoM/Extensions/PythonEnvironments")
        {
            if (!Query.ValidEnvironmentName(name))
            {
                BH.Engine.Base.Compute.RecordError("Invalid BHoM PythonEnvironment name.");
                return null;
            }

            if (Query.EnvironmentExists(name))
            {
                BH.Engine.Base.Compute.RecordError($"A BHoM Python Environment named {name} already exists.");
                return null;
            }

            // create the directory in which Python will be installed
            string targetDirectory = Path.Combine(directory, name);
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
            if (additionalPackage != null)
            {
                string result = Compute.InstallLocalPackage(executable, additionalPackage);
            }

            // install ipykernel and register environment with the base BHoM Python environment
            Compute.InstallPackages(executable, new List<string>() { "ipykernel" });
            string kernelCreateCmd = $"{Modify.AddQuotesIfRequired(executable)} -m ipykernel install --name={name}";
            string kernelRegistry = Compute.RunCommandStdout(kernelCreateCmd);

            return new oM.Python.PythonEnvironment(){ Name = name, Executable = executable };
        }
    }
}
