/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
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
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Generate a TOML file suitable for creating a Python environment. This is only intended for custom virtual environments, and should not be used for creation of toolkit-specific environments which should have their own fixed *.toml files where versioning and packages are managed centrally.")]
        [Input("version", "The target version of python to be installed or retrieved.")]
        [Input("name", "The name of the Python project.")]
        [Input("packages", "A list of Python packages to be included in the environment.")]
        [Input("directory", "The directory where the TOML file should be generated.")]
        [Output("tomlFile", "The path to the generated TOML file.")]
        public static string GenerateTOML(
            PythonVersion version,
            string name,
            IEnumerable<string> packages,
            string directory
        )
        {
            if (string.IsNullOrWhiteSpace(directory))
                throw new ArgumentException("directory cannot be empty.", nameof(directory));
            Directory.CreateDirectory(directory);

            // get the Python version string
            FieldInfo field = version.GetType().GetField(version.ToString());
            string pythonVersion = field?.GetCustomAttribute<DescriptionAttribute>()?.Description;
            var v = Version.Parse(pythonVersion);
            string lower = $"{v.Major}.{v.Minor}";
            string upper = $"{v.Major}.{v.Minor + 1}";
            string pythonVersionString = $">={lower},<{upper}";

            string filePath = Path.Combine(directory, "pyproject.toml");

            var sb = new StringBuilder();

            sb.AppendLine("[project]");
            sb.AppendLine($"name = \"{name}\"");
            sb.AppendLine("version = \"0.1.0\"");
            sb.AppendLine($"requires-python = \"{pythonVersionString}\"");
            sb.AppendLine();

            sb.AppendLine("dependencies = [");
            foreach (string package in packages ?? Enumerable.Empty<string>())
            {
                sb.AppendLine($"    \"{package}\",");
            }
            sb.AppendLine("]");

            File.WriteAllText(filePath, sb.ToString());

            return filePath;
        }
    }
}
