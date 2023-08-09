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
using BH.oM.Python.Enums;
using System;
using System.ComponentModel;
using System.IO;
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

        // TODO - THIS METHOD HAS CHANGED BUT IS STILL USED, SO NEEDS DEPRECATING
        [Description("Download the target version of Python.")]
        [Input("version", "A Python version.")]
        [Output("executablePath", "The path of the executable for the downloaded Python.")]
        [PreviousVersion("6.3", "BH.Engine.Python.Compute.DownloadPython(this BH.oM.Python.Enums.PythonVersion)")]
        public static string DownloadPython(this PythonVersion version, string name = null)
        {
            string url = version.EmbeddableURL();
            if (string.IsNullOrEmpty(name))
                name = Path.GetFileNameWithoutExtension(url);
            string targetExecutable = Path.Combine(Query.DirectoryEnvironments(), name, "python.exe");
            
            if (File.Exists(targetExecutable))
                return targetExecutable;
            
            string zipfile = DownloadFile(url, Query.DirectoryEnvironments());
            UnzipFile(zipfile, Query.DirectoryEnvironments(), name, true);

            return targetExecutable;
        }

        [Description("Download the pip installer")]
        [Input("targetDirectory", "The directory into which get-pip.py will be downloaded.")]
        [Output("getpipPath", "The path of the file used to install pip into an embedded Python environment.")]
        public static string DownloadGetPip(string targetDirectory)
        {
            return DownloadFile("https://bootstrap.pypa.io/get-pip.py", targetDirectory);
        }
    }
}
