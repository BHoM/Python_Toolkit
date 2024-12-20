/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2025, the respective contributors. All rights reserved.
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
using BH.oM.Python.Enums;
using System;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Xml.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Download a file from a Url.")]
        [Input("fileUrl", "The file to download.")]
        [Input("targetDirectory", "The destination directory to download the file to.")]
        [Input("filename", "An optional input to rename the downloaded file.")]
        [Input("overwrite", "An optional input to overwrite the file if it already exists, otherwise if it does then return the existing file.")]
        [Output("filePath", "The path to the downloaded file.")]
        public static string DownloadFile(
            string fileUrl,
            string targetDirectory,
            string filename = null,
            bool overwrite = true
        )
        {
            if (string.IsNullOrWhiteSpace(fileUrl))
            {
                BH.Engine.Base.Compute.RecordError($"The fileUrl cannot be null or empty.");
                return null;
            }
                

            if (string.IsNullOrWhiteSpace(targetDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"The targetDirectory cannot be null or empty.");
                return null;
            }
                

            if (!Directory.Exists(targetDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"The targetDirectory \"{targetDirectory}\" does not exist.");
                return null;
            }
                

            if (string.IsNullOrWhiteSpace(filename))
                filename = Path.GetFileName(fileUrl);

            string filePath = Path.Combine(targetDirectory, filename);

            if (File.Exists(filePath))
            {
                if (!overwrite)
                    return filePath;
                File.Delete(filePath);
            }

            using (var client = new System.Net.WebClient())
            {
                client.DownloadFile(fileUrl, filePath);
            }

            return filePath;
        }

        /******************************************************/

        [Description("Download and install a specified version of python, and return the executable for it.")]
        [Input("version", "The version of python to download.")]
        [Output("pythonExecutable", "The executable (python.exe) for the python version that was installed")]
        public static string DownloadPythonVersion(this PythonVersion version)
        {
            string url = version.EmbeddableURL();

            string basePath = Path.Combine(Query.DirectoryBaseEnvironment(version));

            if (File.Exists(Path.Combine(basePath, "python.exe")))
                return Path.Combine(basePath, "python.exe");

            if (!Directory.Exists(basePath))
                Directory.CreateDirectory(basePath);
            else
            {
                Directory.Delete(basePath, true); //if there are any files here already for some reason, remove them.
                Directory.CreateDirectory(basePath);
            }

            string installerFile = DownloadFile(url, basePath, "installer.exe");

            using (Process install = new Process()
            {
                StartInfo = new ProcessStartInfo()
                {
                    FileName = installerFile,
                    Arguments = $"/passive InstallAllUsers=0 InstallLauncherAllUsers=0 Include_launcher=0 Shortcuts=0 AssociateFiles=0 Include_tools=0 Include_test=0 TargetDir={Modify.AddQuotesIfRequired(basePath)}",
                    RedirectStandardError = true,
                    UseShellExecute = false,
                }
            })
            {
                install.Start();
                string stderr = install.StandardError.ReadToEnd();
                install.WaitForExit();
                if (install.ExitCode != 0)
                {
                    BH.Engine.Base.Compute.RecordError($"Error installing python: {stderr}");
                    return null;
                }
            }

            string pythonExePath = Path.Combine(basePath, "python.exe");

            // It is possible for the installer to exit with ExitCode==0 without installing Python in the requested location. This can happen if the same version of Python appears to be installed elsewhere on the system. It can also happen if there was a 'dodgy' uninstall of a previous version. We've been unable to figure out where the installer is actually looking for existing installs. In lieu of a better solution, to fix dodgy uninstalls, run the installer again for the target version of Python (download links within EmbeddableURL.cs) and run a combination of 'repair' and 'uninstall' until it's gone. Installing the py launcher (via 'modify' in the installer) before attempting to uninstall could also help. 

            if (!File.Exists(pythonExePath))
            {
                BH.Engine.Base.Compute.RecordError($"The Python installer appears to have completed successfully, but \n{pythonExePath} does not exist. \nThis usually means that Python {version} already exists on your machine, but in a different location. \nThis toolkit is therefore unable to run any Python commands right now. \nTry uninstalling Python from your system before running this BHoM method again.");
                return null;
            }

            return pythonExePath;
        }
    }
}


