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
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Gets the Python version for the requested Python executable.")]
        [Input("pythonExecutable", "Path to python.exe.")]
        [Output("version", "Python version of the requested Python executable.")]
        public static PythonVersion Version(string pythonExecutable)
        {
            if (!File.Exists(pythonExecutable)) 
            {
                return PythonVersion.Undefined;
            }

            Process process = new Process()
            {
                StartInfo = new ProcessStartInfo()
                {
                    FileName = pythonExecutable,
                    Arguments = $"--version",
                    RedirectStandardError = true,
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                }
            };

            try
            {
                string versionString;
                using (Process p = Process.Start(process.StartInfo))
                {
                    string standardError = p.StandardError.ReadToEnd();
                    versionString = p.StandardOutput.ReadToEnd().TrimEnd();
                    p.WaitForExit();
                    if (p.ExitCode != 0)
                    {
                        BH.Engine.Base.Compute.RecordError($"Error getting Python version.\n{standardError}");
                        return PythonVersion.Undefined;
                    }
                }

                List<string> strings = versionString.Replace("Python ", "").Replace(".", "_").Split('_').ToList();
                strings.RemoveAt(strings.Count - 1);
                string enumParseable = "v" + strings.Aggregate((a, b) => $"{a}_{b}");

                return (PythonVersion)Enum.Parse(typeof(PythonVersion), enumParseable);
            }
            catch
            {
                return PythonVersion.Undefined;
            }

        }
    }
}


