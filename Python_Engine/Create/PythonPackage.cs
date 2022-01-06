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
using BH.oM.Reflection.Attributes;

using System.ComponentModel;
using System.Linq;
using System;

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Create a BHoM Python package, with additional checks to ensure that it is a valid object.")]
        [Input("name", "The name of the Python package, used to install via Pip.")]
        [Input("version", "The version of the package.")]
        [Output("package", "A BHoM PythonPackage object.")]
        public static PythonPackage PythonPackage(string name, string version)
        {
            if (name == "" || version == "")
            {
                BH.Engine.Reflection.Compute.RecordError($"The package name or version is not valid.");
                return null;
            }

            if (name.Any(x => Char.IsWhiteSpace(x)))
            {
                BH.Engine.Reflection.Compute.RecordError($"A PythonPackage name cannot contain whitespace characters.");
                return null;
            }

            if (version.Any(x => Char.IsWhiteSpace(x)))
            {
                BH.Engine.Reflection.Compute.RecordError($"A PythonPackage version cannot contain whitespace characters.");
                return null;
            }

            return new PythonPackage() { Name = name, Version = version };
        }
    }
}

