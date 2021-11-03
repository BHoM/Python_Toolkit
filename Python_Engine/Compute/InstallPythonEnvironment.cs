/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
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

using BH.oM.Python;
using BH.oM.Reflection.Attributes;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install the BHoM Python environment.")]
        [Input("pythonEnvironment", "A BHoM Python environment.")]
        [Input("force", "If the environment already exists recreate it rather than re-using it.")]
        [Input("run", "Set to True to run the PythonEnvironment installer.")]
        [Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        public static PythonEnvironment InstallPythonEnvironment(this PythonEnvironment pythonEnvironment, bool force = false, bool run = false)
        {
            if (!run)
                return null;

            // load existing environment if it matches the requested environment
            PythonEnvironment existingEnvironment = Query.LoadPythonEnvironment(pythonEnvironment.Name);
            if (existingEnvironment.IsInstalled())
            {
                if (!force)
                {
                    if (existingEnvironment.Version != pythonEnvironment.Version)
                    {
                        BH.Engine.Reflection.Compute.RecordError($"An environment exists with the given name, but its Python version does not match the given version. To overwrite this existing environment set \"force\" to True.");
                        return null;
                    }

                    // check that the existing environment contains the packages requested
                    List<PythonPackage> existingPackages = existingEnvironment.Packages;
                    foreach (PythonPackage pkg in pythonEnvironment.Packages)
                    {
                        if (!existingPackages.PackageInList(pkg))
                        {
                            BH.Engine.Reflection.Compute.RecordError($"An environment exists with the given name, but it doesn't contain {pkg.GetString()}. To overwrite this existing environment set \"force\" to True.");
                            return null;
                        }
                    }
                    return existingEnvironment;
                }
                else
                {
                    existingEnvironment.RemoveEnvironment(true);
                }
            }

            // create the new environment directory
            string environmentDirectory = pythonEnvironment.EnvironmentDirectory();
            System.IO.Directory.CreateDirectory(environmentDirectory);

            // download the target version of Python
            string embeddablePythonZip = Compute.DownloadFile(pythonEnvironment.Version.EmbeddableURL());

            // extract embeddable python into environment directory
            System.IO.Compression.ZipFile.ExtractToDirectory(embeddablePythonZip, environmentDirectory);

            // run the pip installer
            string pipInstallerPy = Compute.DownloadFile("https://bootstrap.pypa.io/get-pip.py");
            string installPipCommand = $"{pythonEnvironment.PythonExecutable()} {pipInstallerPy} && exit";
            if (!Compute.RunCommandBool(installPipCommand, hideWindows: true))
            {
                BH.Engine.Reflection.Compute.RecordError($"Pip installation did not work using the command {installPipCommand}.");
                return null;
            }

            // remove _pth file
            List<string> pthFiles = System.IO.Directory.GetFiles(environmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith("._pth")).ToList();
            foreach (string pthFile in pthFiles)
            {
                try
                {
                    File.Delete(pthFile);
                }
                catch (Exception e)
                {
                    BH.Engine.Reflection.Compute.RecordError($"{pthFile} not found to be deleted: {e}.");
                    return null;
                }
            }

            // move PYD and DLL files to DLLs directory
            string libDirectory = System.IO.Directory.CreateDirectory(Path.Combine(environmentDirectory, "DLLs")).FullName;
            List<string> libFiles = System.IO.Directory.GetFiles(environmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => (s.EndsWith(".dll") || s.EndsWith(".pyd")) && !Path.GetFileName(s).Contains("python") && !Path.GetFileName(s).Contains("vcruntime")).ToList();
            foreach (string libFile in libFiles)
            {
                string newLibFile = Path.Combine(libDirectory, Path.GetFileName(libFile));
                try
                {
                    File.Move(libFile, newLibFile);
                }
                catch (Exception e)
                {
                    BH.Engine.Reflection.Compute.RecordError($"{libFile} not capable of being moved to {newLibFile}: {e}.");
                    return null;
                }
            }

            // install packages using Pip
            pythonEnvironment = pythonEnvironment.InstallPythonPackages(pythonEnvironment.Packages, force: true, run: true);

            return pythonEnvironment;

        }
    }
}
