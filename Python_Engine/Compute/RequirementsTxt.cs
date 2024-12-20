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
using System.Diagnostics;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Create a requirements.txt file from an existing Python executable.")]
        [Input("executable", "The path to the Python executable to create the requirements.txt file from.")]
        [Input("targetPath", "The path to the requirements.txt file to create. If not specified, the file will be created in the same directory as the executable.")]
        [Output("requirementsTxt", "The path to the requirements.txt file.")]
        public static string RequirementsTxt(
            string executable,
            string targetPath = null
        )
        {
            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError($"The executable '{executable}' does not exist.");
                return null;
            }

            if (string.IsNullOrEmpty(targetPath))
            {
                targetPath = Path.Combine(Path.GetDirectoryName(executable), "requirements.txt");
            }
            else
            {
                if (!Directory.Exists(Path.GetDirectoryName(targetPath)))
                {
                    BH.Engine.Base.Compute.RecordError($"The executable '{executable}' does not exist.");
                    return null;
                }
            }

            System.Diagnostics.Process process = new System.Diagnostics.Process()
            {
                StartInfo = new System.Diagnostics.ProcessStartInfo()
                {
                    FileName = executable,
                    Arguments = $"-m pip freeze",
                    UseShellExecute = false,
                    RedirectStandardError = true,
                    RedirectStandardOutput = true
                }
            };
            using (Process p = Process.Start(process.StartInfo))
            {
                StreamWriter sr = new StreamWriter(targetPath);
                sr.Write(p.StandardOutput.ReadToEnd());
                string standardError = p.StandardError.ReadToEnd();
                p.WaitForExit();
                if (p.ExitCode != 0)
                    BH.Engine.Base.Compute.RecordError($"Error creating requirements.txt from \"{executable}\".\n{standardError}");
                sr.Close();
            }

            return targetPath;
        }
    }
}


