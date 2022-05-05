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

using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System;
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
            {
                BH.Engine.Base.Compute.RecordNote($"This component will install a Python environment for {pythonEnvironment.Name} if it doesn't exist, or return the existing environment if it does.");
                return null;
            }

            string basePythonExe = $"{Query.EnvironmentsDirectory()}\\Python_Toolkit\\python.exe";
            string basePythonDir = $"{Query.EnvironmentsDirectory()}\\Python_Toolkit";

            // load existing environment if it matches the requested environment
            PythonEnvironment existingEnvironment = Query.LoadPythonEnvironment(pythonEnvironment.Name);
            if (existingEnvironment.IsInstalled())
            {
                if (!force)
                {
                    if (existingEnvironment.Version != pythonEnvironment.Version)
                    {
                        BH.Engine.Base.Compute.RecordError($"An environment exists with the given name, but its Python version does not match the given version. To overwrite this existing environment set \"force\" to True.");
                        return null;
                    }

                    // check that the existing environment contains the packages requested
                    List<PythonPackage> existingPackages = existingEnvironment.Packages;
                    foreach (PythonPackage pkg in pythonEnvironment.Packages)
                    {
                        if (!existingPackages.PackageInList(pkg))
                        {
                            BH.Engine.Base.Compute.RecordError($"An environment exists with the given name, but it doesn't contain {pkg.GetString()}. To overwrite this existing environment set \"force\" to True.");
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
                BH.Engine.Base.Compute.RecordError($"Pip installation did not work using the command {installPipCommand}.");
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
                    BH.Engine.Base.Compute.RecordError($"{pthFile} not found to be deleted: {e}.");
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
                    BH.Engine.Base.Compute.RecordError($"{libFile} not capable of being moved to {newLibFile}: {e}.");
                    return null;
                }
            }

            // install packages using Pip
            pythonEnvironment = pythonEnvironment.InstallPythonPackages(pythonEnvironment.Packages, force: true, run: true);

            // prepend PythonCode directory to Jupyter Notebook Path
            string ipythonPrependCmd = $"\"{basePythonExe}\" -m IPython profile create\n";
            string ipythonPrependBatPath = System.IO.Path.Combine(Path.GetTempPath(), "ipython_path_prepend.bat");
            File.WriteAllText(ipythonPrependBatPath, ipythonPrependCmd);
            System.Diagnostics.Process ipythonPrependProcess = new System.Diagnostics.Process();
            ipythonPrependProcess.StartInfo = new System.Diagnostics.ProcessStartInfo(
                "cmd.exe", "/c " + ipythonPrependBatPath
            ) {
                CreateNoWindow = true, 
                UseShellExecute = false, 
                RedirectStandardError = true, 
                RedirectStandardOutput = true 
            };
            ipythonPrependProcess.Start();
            ipythonPrependProcess.WaitForExit();
            File.Delete(ipythonPrependBatPath);
            File.WriteAllText(
                $"C:\\Users\\{System.Environment.UserName}\\.ipython\\profile_default\\ipython_config.py", 
                $"c.InteractiveShellApp.exec_lines = ['import sys; sys.path.insert(0, r\"{Query.CodesDirectory()}\")']"
            );
            File.WriteAllText(
                $"C:\\Users\\{System.Environment.UserName}\\.ipython\\profile_default\\startup\\bhom_python_code.py",
                $"import sys; sys.path.insert(0, r\"{Query.CodesDirectory()}\")"
            );

            // register environment with ipykernel
            if (pythonEnvironment.Name != "Python_Toolkit")
            {
                // create the kernel for the python environment being installed and point towards the environment executable
                string kernelCreateCmd = $"\"{basePythonExe}\" -m ipykernel install --name={pythonEnvironment.Name} --prefix \"{basePythonDir}\"\n";
                string kernelCreateBatPath = System.IO.Path.Combine(Path.GetTempPath(), "ipykernel_register.bat");
                File.WriteAllText(kernelCreateBatPath, kernelCreateCmd);
                System.Diagnostics.ProcessStartInfo kernelProcessInfo = new System.Diagnostics.ProcessStartInfo("cmd.exe", "/c " + kernelCreateBatPath);
                kernelProcessInfo.CreateNoWindow = true;
                kernelProcessInfo.UseShellExecute = false;
                kernelProcessInfo.RedirectStandardError = true;
                kernelProcessInfo.RedirectStandardOutput = true;
                System.Diagnostics.Process kernelProcess = new System.Diagnostics.Process();
                kernelProcess.StartInfo = kernelProcessInfo;
                kernelProcess.Start();
                kernelProcess.WaitForExit();
                File.Delete(kernelCreateBatPath);

                // modify kernel.json to set the path to be that of the current pythonEnvironments executable
                string kernelConfigFile = $"{basePythonDir}\\share\\jupyter\\kernels\\{pythonEnvironment.Name.ToLower()}\\kernel.json";
                string text = File.ReadAllText(kernelConfigFile);
                text = text.Replace("C:\\\\ProgramData\\\\BHoM\\\\Extensions\\\\PythonEnvironments\\\\Python_Toolkit\\\\python.exe", $"C:\\\\ProgramData\\\\BHoM\\\\Extensions\\\\PythonEnvironments\\\\{pythonEnvironment.Name}\\\\python.exe");
                File.WriteAllText(kernelConfigFile, text);
            }

            return pythonEnvironment;

        }

        [Description("Install the default BHoM Python_Toolkit environment.")]
        [Input("run", "Set to True to run the PythonEnvironment installer.")]
        [Input("force", "If the environment already exists recreate it rather than re-using it.")]
        [Input("configJSON", "Path to a config JSON containing Python environment configuration.")]
        [Output("pythonEnvironment", "The default BHoM Python_Toolkit environment object.")]
        public static PythonEnvironment InstallPythonEnvironment(bool run = false, bool force = false, string configJSON = @"C:\ProgramData\BHoM\Settings\Python\Python_Toolkit.json")
        {
            // Install base Python environment if it doesnt already exist
            PythonEnvironment basePythonEnvironment = Create.PythonEnvironment(@"C:\ProgramData\BHoM\Settings\Python\Python_Toolkit.json");
            basePythonEnvironment.InstallPythonEnvironment(force, run);

            PythonEnvironment toolkitPythonEnvironment = Create.PythonEnvironment(configJSON);
            return toolkitPythonEnvironment.InstallPythonEnvironment(force, run);
        }
    }
}

