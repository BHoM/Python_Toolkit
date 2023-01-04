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
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Download a target version of Python.")]
        [Input("version", "A Python version.")]
        [Output("executablePath", "The path of the executable for the downloaded Python.")]
        [PreviousVersion("5.3", "BH.Engine.Python.Compute.DownloadPython()")]
        public static string DownloadPython(this BH.oM.Python.Enums.PythonVersion version)
        {
            string targetDirectory = Query.EnvironmentsDirectory();
            string versionString = version.ToString().Replace("v", "");
            string resultantDirectory = Path.Combine(targetDirectory, versionString);
            string executable = Path.Combine(resultantDirectory, "python.exe");

            if (File.Exists(executable))
                return executable;

            string pythonUrl = version.EmbeddableURL();
            string pythonZipFile = Path.Combine(targetDirectory, Path.GetFileName(pythonUrl));

            List<string> commands = new List<string>()
            {
                $"curl {pythonUrl} -o {pythonZipFile}",
                $"mkdir {resultantDirectory}",
                $"tar -v -xf {pythonZipFile} -C {resultantDirectory}",
                $"del {pythonZipFile}",
            };
            foreach (string command in commands)
	        {
                RunCommandStdout(command, hideWindows: true);
	        }

            return executable;
        }
    }
}


