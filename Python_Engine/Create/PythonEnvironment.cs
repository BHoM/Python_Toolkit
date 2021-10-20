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
        [Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        // TODO - split environment creation methods up into smaller parts to make more manageable
        public static PythonEnvironment PythonEnvironment(string name, string version, List<string> packages = null)
        {
            PythonEnvironment pythonEnvironment = new PythonEnvironment
            {
                Name = name
            };

            // create environment directory
            string environmentDirectory = pythonEnvironment.EnvironmentDirectory();

            // download the target version of Python
            string embeddablePythonZip = Compute.DownloadFile(Query.EmbeddableURL(version));

            // extract embeddable python into environment directory
            System.IO.Compression.ZipFile.ExtractToDirectory(embeddablePythonZip, environmentDirectory);

            // set up the environment following inflation of the embeddable zip
            // TODO - see https://dev.to/fpim/setting-up-python-s-windows-embeddable-distribution-properly-1081
            string pipInstallerPy = Compute.DownloadFile("https://bootstrap.pypa.io/get-pip.py");

            // run the pip installer
            string installPipCommand = $"{pythonEnvironment.PythonExecutable()} {pipInstallerPy} && exit";
            if (!Compute.RunCommandBool(installPipCommand, hideWindows: true))
            {
                BH.Engine.Reflection.Compute.RecordError($"Pip installation did not work using the command {installPipCommand}.");
                return null;
            }

            // remove _pth file
            // string pthFile = System.IO.Directory.GetFiles(environmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith("._pth")).ToList().First();
            // string pthText = File.Delete(pthFile);

            // move pyd and dll files to DLLs directory
            string[] filesToMove = System.IO.Directory.GetFiles(environmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => (s.EndsWith(".dll") || s.EndsWith(".pyd")) && !Path.GetFileName(s).Contains("python") && !Path.GetFileName(s).Contains("vcruntime")).ToArray();
            // TODO - move files
            string zipFile = System.IO.Directory.GetFiles(environmentDirectory, "*.*", SearchOption.TopDirectoryOnly).Where(s => s.EndsWith(".zip")).First();
            File.Delete(zipFile);

            string tempDir = Path.Combine(environmentDirectory, "temp");
            string newDir = Path.Combine(environmentDirectory, Path.GetFileName(zipFile));
            System.IO.Compression.ZipFile.ExtractToDirectory(embeddablePythonZip, tempDir);
            
            System.IO.Directory.Move(tempDir, newDir);

            // install packages using Pip
            if (!packages?.Any() != true)
            {
                foreach (string package in packages)
                {
                    if (!Compute.RunCommandBool($"{pythonEnvironment.PythonExecutable()} -m pip install --no-warn-script-location {package} && exit"))
                    {
                        BH.Engine.Reflection.Compute.RecordError($"{package} not installed for some reason.");
                    }
                }
            }

            return pythonEnvironment;
        }
    }
}
