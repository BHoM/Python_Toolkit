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

using BH.oM.Python;
using BH.oM.Reflection.Attributes;
using System.ComponentModel;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Create the BHoM Python environment directory.")]
        [Input("pythonEnvironment", "A BHoM Python environment object.")]
        [Output("environmentDirectory", "The full path to the BHoM Python environment.")]
        private static string EnvironmentDirectory(this PythonEnvironment pythonEnvironment)
        {
            if (System.String.IsNullOrEmpty(pythonEnvironment.Name))
            {
                BH.Engine.Reflection.Compute.RecordError($"The given PythonEnvironment hasn't got a name.");
                return null;
            }

            if (pythonEnvironment.Name.Any(x => System.Char.IsWhiteSpace(x)))
            {
                BH.Engine.Reflection.Compute.RecordError($"The given PythonEnvironment name cannot contain whitespace characters.");
                return null;
            }

            string environmentDirectory = System.IO.Path.Combine(pythonEnvironment.RootDirectory, pythonEnvironment.Name);
            System.IO.Directory.CreateDirectory(environmentDirectory);

            return environmentDirectory;
        }
    }
}
