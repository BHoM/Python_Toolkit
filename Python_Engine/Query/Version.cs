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
using BH.oM.Python;
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
        public static string Version(string pythonExecutable)
        {
            if (!File.Exists(pythonExecutable))
            {
                BH.Engine.Base.Compute.RecordError(new FileNotFoundException(), $"No file found at {pythonExecutable}");
            }

            string result = BH.Engine.Python.Compute.RunCommandStdout(command: $"{pythonExecutable} --version");
            return result.Replace("Python ", "");
        }

        [Description("Get the Python version for the installed PythonEnvironment.")]
        [Input("venv", "The PythonEnvironment.")]
        [Output("version", "Python version of the installed PythonEnvironment.")]
        public static string Version(this PythonEnvironment venv)
        {
            return Version(venv.Executable);
        }
    }
}
