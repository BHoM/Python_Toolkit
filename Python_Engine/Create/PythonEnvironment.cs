﻿/*
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
using System.Text;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Install the embeddable Python into the target directory.")]
        [Input("name", "The name of the directory into which Python will be installed.")]
        [Input("version", "The version of Python to be installed.")]
        [Input("packages", "A list of packages to be installed into this Python environment.")]
        [Input("force", "If the environment already exists recreate it rather than re-using it.")]
        [Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        public static PythonEnvironment PythonEnvironment(string name, string version, List<string> packages = null, bool force = false)
        {

            // force the user to be specific with their package versioning.
            foreach (string package in packages)
            {
                if (!package.Contains("=="))
                {
                    BH.Engine.Reflection.Compute.RecordError($"BHoM Python environments should be specific with the version of each package being used. Your {package} package must include a version number.");
                    return null;
                }
            }

            // Query existing environment if it already exists
            PythonEnvironment existingEnvironment = Query.PythonEnvironment(name);

            if (!(existingEnvironment is null))
            {
                string existingVersion = Query.Version(existingEnvironment);
                if (!String.Equals(version, existingVersion, StringComparison.OrdinalIgnoreCase))
                {
                    if (force)
                    {
                        Compute.RemoveEnvironment(existingEnvironment);
                        return Create.PythonEnvironment(name, version, packages);

                    }
                    else
                    {
                        BH.Engine.Reflection.Compute.RecordError($"The requested environment already exists, but the version of Python does not match the requested version ({version}!={existingVersion}). Set force to True to recreate this environment with the given version.");
                        return null;
                    }
                }
                else
                {
                    foreach (string package in packages)
                    {
                        if (!existingEnvironment.IsPackageInstalled(package))
                        {
                            if (force)
                            {
                                Compute.RemoveEnvironment(existingEnvironment);
                                return Create.PythonEnvironment(name, version, packages);
                            }
                            else
                            {
                                BH.Engine.Reflection.Compute.RecordError($"The requested environment already exists, but its packages do no match the requested package versions. Set force to True to recreate this environment with the new package versions.");
                                return null;
                            }
                        }
                    }
                }
                return existingEnvironment;
            }
            else
            {
                PythonEnvironment pythonEnvironment = new PythonEnvironment
                {
                    Name = name
                };

                // create environment directory
                string environmentDirectory = Create.EnvironmentDirectory(pythonEnvironment);

                // download the target version of Python
                string embeddablePythonZip = Compute.DownloadFile(Query.EmbeddableURL(version));

                // extract embeddable python into environment directory
                System.IO.Compression.ZipFile.ExtractToDirectory(embeddablePythonZip, environmentDirectory);

                // set up the environment following inflation of the embeddable zip
                string pipInstallerPy = Compute.DownloadFile("https://bootstrap.pypa.io/get-pip.py");

                // run the pip installer
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
                    }
                }

                // install packages using Pip
                if (!packages?.Any() != true)
                {
                    if (!Compute.RunCommandBool($"{pythonEnvironment.PythonExecutable()} -m pip install --no-warn-script-location {String.Join(" ", packages)} && exit", hideWindows: true))
                    {
                        BH.Engine.Reflection.Compute.RecordError($"Packages not installed for some reason.");
                    }
                }

                return pythonEnvironment;
            }
        }
    }
}