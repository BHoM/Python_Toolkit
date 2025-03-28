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
using System;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        //This method is no longer used by python toolkit, and perhaps should be removed or moved to the file toolkit instead.
        [Description("Extract the contents of an archive.")]
        [Input("archivePath", "The archive to extract.")]
        [Input("targetDirectory", "The destination directory to extract into.")]
        [Input("targetName", "An optional input to rename the archive directory.")]
        [Input("delete", "An optional input to delete the archive after extraction.")]
        public static void UnzipFile(
            string archivePath,
            string targetDirectory,
            string targetName = null,
            bool delete = false
        )
        {
            if (string.IsNullOrWhiteSpace(archivePath))
            {
                BH.Engine.Base.Compute.RecordError($"The archivePath cannot be null or empty.");
            }

            if (string.IsNullOrWhiteSpace(targetDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"The targetDirectory cannot be null or empty.");
            }

            if (!File.Exists(archivePath))
            {
                BH.Engine.Base.Compute.RecordError($"The archivePath '{archivePath}' does not exist.");
            }

            if (!Directory.Exists(targetDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"The targetDirectory '{targetDirectory}' does not exist.");
            }

            if (string.IsNullOrWhiteSpace(targetName))
            {
                targetName = Path.GetFileNameWithoutExtension(archivePath);
            }

            string targetPath = Path.Combine(targetDirectory, targetName);

            if (Directory.Exists(targetPath))
            {
                BH.Engine.Base.Compute.RecordError($"The targetPath '{targetPath}' already exists.");
            }

            System.IO.Compression.ZipFile.ExtractToDirectory(archivePath, targetPath);
            
            if (delete)
                File.Delete(archivePath);
        }
    }
}


