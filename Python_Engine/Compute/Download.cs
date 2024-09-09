/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2024, the respective contributors. All rights reserved.
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
        /*
        // TODO - THIS METHOD HAS CHANGED BUT IS STILL USED, SO NEEDS DEPRECATING
        // changed from what to what ?
        [Description("Download the installer for the target version of python.")]
        [Input("version", "A Python version.")]
        [Input("name", "Name of the toolkit for this installation of python.")]
        [Output("executablePath", "The path of the executable for the downloaded Python installer.")]
        public static string DownloadPython(this PythonVersion version, string name = null)
        {
            string url = version.EmbeddableURL();
            if (string.IsNullOrEmpty(name))
                name = Path.GetFileNameWithoutExtension(url);

            string targetExecutable = Path.Combine(Query.DirectoryBaseEnvironment(), version.ToString(), "installer.exe");

            if (File.Exists(targetExecutable))
                return targetExecutable;

            if (!Directory.Exists(Path.Combine(Query.DirectoryEnvironments(), name)))
                Directory.CreateDirectory(Path.Combine(Query.DirectoryEnvironments(), name));

            string exefile = DownloadFile(url, Path.Combine(Query.DirectoryEnvironments(), name));

            return exefile;
        }*/

        [PreviousVersion("7.3", "BH.Engine.Python.Compute.DownloadPython(BH.oM.Python.PythonVersion, System.String)")]
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

            return Path.Combine(basePath, "python.exe");
        }
    }
}

