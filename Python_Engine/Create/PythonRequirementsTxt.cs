/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2022, the respective contributors. All rights reserved.
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

using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.ComponentModel;
using System.Linq;
using System;
using System.Collections.Generic;
using System.Text;

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Create a requirements.txt file for use in creating a Python envrionment outside of BHoM.")]
        [Input("pythonEnvironment", " A BHoM PythonEnvironment object.")]
        [Input("directory", "The directory in which the requirements.txt file should be written.")]
        [Output("file", "The created requirements.txt file.")]
        public static string PythonRequirementsTxt(this PythonEnvironment pythonEnvironment, string directory)
        {
            return pythonEnvironment.Packages.PythonRequirementsTxt(directory);
        }

        [Description("Create a requirements.txt file for use in creating a Python envrionment outside of BHoM.")]
        [Input("packages", " A list of Python packages to incude in the requirements.txt file.")]
        [Input("directory", "The directory in which the requirements.txt file should be written.")]
        [Output("file", "The created requirements.txt file.")]
        public static string PythonRequirementsTxt(this List<PythonPackage> packages, string directory)
        {
            string requirementsFile = $"{directory}\\requirements.txt";

            StringBuilder sb = new StringBuilder();
            foreach (PythonPackage pkg in packages)
            {
                sb.AppendLine($"{pkg.Name}=={pkg.Version}");
            }
            System.IO.File.WriteAllText(requirementsFile, sb.ToString());

            return requirementsFile;
        }
    }
}

