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
        [Description("Install a Python Virtual Environment of a given version and name.")]
        [Input("version", "The version of Python to use for this environment.")]
        [Input("name", "The name of this virtualenv.")]
        [Input("reload", "Reload the virtual environment rather than recreating it, if it already exists.")]
        [Output("env", "The exectuble for the resultant virtualenv.")]
        public static PythonEnvironment VirtualEnvironment(this PythonVersion version, string name, bool reload = true)
        {
            if (!Query.IsValidEnvironmentName(name))
            {
                BH.Engine.Base.Compute.RecordError("A BHoM Python virtual environment cannot cannot contain invalid filepath characters.");
                return null;
            }
            if (version == PythonVersion.Undefined)
            {
                BH.Engine.Base.Compute.RecordError("Please provide a version of Python.");
                return null;
            }

            // check that base environment is installed and return null and raise error if it isn't
            string baseEnvironmentExecutable = Path.Combine(Query.DirectoryBaseEnvironment(), "python.exe");
            if (!File.Exists(baseEnvironmentExecutable))
            {
                BH.Engine.Base.Compute.RecordWarning("The base Python environment doesnt seem to be installed. Install it first in order to run this method.");
                return null;
            }

            string targetExecutable = Query.VirtualEnvironmentExecutable(name);
            string targetDirectory = Query.VirtualEnvironmentDirectory(name);
            bool exists = Query.VirtualEnvironmentExists(name);

            if (exists && reload)
                return new PythonEnvironment() { Name = name, Executable = targetExecutable };

            if (exists && !reload)
            {
                // remove all existing environments and kernels
                RemoveVirtualEnvironment(name);
                RemoveKernel(name);
            }

            // download the target version of Python
            string referencedExecutable = version.DownloadPython();
            
            // move the directory containing referencedExecutable into Query.DirectoryBaseEnvironment() using the same name
            string sourceDirectory = Path.GetDirectoryName(referencedExecutable);
            string destinationDirectory = Path.Combine(Query.DirectoryBaseEnvironment(), new DirectoryInfo(Path.GetDirectoryName(referencedExecutable)).Name);
            if (!Directory.Exists(destinationDirectory))
            {
                Directory.Move(sourceDirectory, destinationDirectory);
            }
            if (Directory.Exists(sourceDirectory))
                Directory.Delete(sourceDirectory, true);
            referencedExecutable = Path.Combine(destinationDirectory, "python.exe");

            // create the venv from the base environment
            Process process = new Process()
            {
                StartInfo = new ProcessStartInfo()
                {
                    FileName = Modify.AddQuotesIfRequired(baseEnvironmentExecutable),
                    Arguments = $"-m virtualenv --python={Modify.AddQuotesIfRequired(referencedExecutable)} {Modify.AddQuotesIfRequired(targetDirectory)}",
                    RedirectStandardError = true,
                    UseShellExecute = false,
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error creating virtual environment.\n{p.StandardError.ReadToEnd()}");
            }

            // install ipykernel, pytest and black into new virtualenv
            InstallPackages(targetExecutable, new List<string>() { "ipykernel", "pytest", "black" });

            // register the virtualenv with the base environment
            Process process2 = new Process()
            {
                StartInfo = new ProcessStartInfo()
                {
                    FileName = targetExecutable,
                    Arguments = $"-m ipykernel install --name={name}",
                    RedirectStandardError = true,
                    UseShellExecute = false,
                }
            };
            using (Process p = Process.Start(process2.StartInfo))
            {
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error registering the \"{name}\" virtual environment.\n{p.StandardError.ReadToEnd()}");
            }
            // replace text in a file


            return new PythonEnvironment() { Executable = targetExecutable, Name = name };
        }
    }
}
