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

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Move *.dll and *.pyd files in the base Python environment into a DLL folder in that base environments root directory. This enables \"virtualenv\" to function properly as it expects a non-embeddable version of Python which would create this DLL folder by default.")]
        public static void TidyEmbeddedPython()
        {
            string pythonHome = Query.EmbeddedPythonHome();

            if (!File.Exists(Path.Combine(pythonHome, $"DLLs")))
                Directory.CreateDirectory(Path.Combine(pythonHome, $"DLLs"));
            List<string> filesToMove = new List<string>();
            filesToMove.AddRange(Directory.GetFiles(pythonHome, "*.dll"));
            filesToMove.AddRange(Directory.GetFiles(pythonHome, "*.pyd"));
            foreach (string file in filesToMove)
            {
                if (!file.Contains("python3") && !file.Contains("vcruntime"))
                {
                    File.Move(file, Path.Combine(Path.GetDirectoryName(file), "DLLs", Path.GetFileName(file)));
                }
            }
        }

        /***************************************************/
    }
}