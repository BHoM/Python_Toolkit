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
using BH.oM.Python.Enums;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Retrieve or reinstall the base Python Environment for BHoM workflows.")]
        [Input("reload", "Reload the base Python environment rather than recreating it, if it already exists.")]
        [Output("env", "The base Python Environment for all BHoM workflows.")]
        [PreviousVersion("6.3", "BH.Engine.Python.Compute.InstallBasePythonEnvironment(System.Boolean)")]
        public static PythonEnvironment BasePythonEnvironment(
            bool reload = true
        )
        {
            if (!Directory.Exists(Query.DirectoryEnvironments()))
                // create PythonEnvironments directory if it doesnt already exist
                Directory.CreateDirectory(Query.DirectoryEnvironments());
            
            // determine whether the base environment already exists
            string targetExecutable = Path.Combine(Query.DirectoryBaseEnvironment(), "python.exe");
            bool exists = Directory.Exists(Query.DirectoryBaseEnvironment()) && File.Exists(targetExecutable);

            if (exists && reload)
                return new PythonEnvironment() { Name = Query.ToolkitName(), Executable = targetExecutable };

            if (exists && !reload)
                // remove all existing environments and kernels
                RemoveEverything();

            // download the target Python version and convert into a "full" python installation bypassing admin rights
            string executable = PythonVersion.v3_10_5.DownloadPython(Query.ToolkitName());
            string pipInstaller = DownloadGetPip(Path.GetDirectoryName(executable));
            string baseEnvironmentDirectory = Path.GetDirectoryName(executable);

            // install pip into the python installation
            Process process = new Process()
            {
                StartInfo = new ProcessStartInfo()
                {
                    FileName = Modify.AddQuotesIfRequired(executable),
                    Arguments = Modify.AddQuotesIfRequired(pipInstaller) + " --no-warn-script-location",
                    RedirectStandardError=true,
                    UseShellExecute=false,
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error installing pip.\n{p.StandardError.ReadToEnd()}");
                File.Delete(pipInstaller);
            }

            // delete files with the suffix ._pth from installedDirectory
            List<string> pthFiles = Directory.GetFiles(baseEnvironmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith("._pth")).ToList();
            foreach (string pthFile in pthFiles)
            {
                File.Delete(pthFile);
            }

            // move files with the suffix .dll and .pyd from installedDirectory into a DLLs directory
            string libDirectory = Directory.CreateDirectory(Path.Combine(baseEnvironmentDirectory, "DLLs")).FullName;
            List<string> libFiles = Directory.GetFiles(baseEnvironmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => (s.EndsWith(".dll") || s.EndsWith(".pyd")) && !Path.GetFileName(s).Contains("python") && !Path.GetFileName(s).Contains("vcruntime")).ToList();
            foreach (string libFile in libFiles)
            {
                File.Move(libFile, Path.Combine(libDirectory, Path.GetFileName(libFile)));
            }

            // install essential packages into base environment
            InstallPackages(executable, new List<string>() { "virtualenv", "jupyterlab", "black", "pylint" });

            return new PythonEnvironment() { Name = Query.ToolkitName(), Executable = executable };
        }
    }
}
