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

namespace BH.Engine.Python
{
    public static partial class Convert
    {
        [Description("Get the string representation of BHoM PythonPackage object.")]
        [Input("package", "A BHoM PythonPackage object.")]
        [Output("string", "The Python Pip string representation of a BHoM PythonPackage.")]
        public static string GetString(this PythonPackage package)
        {
            if (package.Name == "" || package.Version == "")
            {
                BH.Engine.Reflection.Compute.RecordError("The package is not valid as it does not contain either a name or version.");
                return "";
            }
            return $"{package.Name}=={package.Version}";
        }

        [Description("Get the string representation of BHoM PythonEnvironment object.")]
        [Input("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        [Output("string", "The string representation of a BHoM PythonEnvironment.")]
        public static string GetString(this PythonEnvironment pythonEnvironment)
        {
            if (pythonEnvironment.Name == "" || pythonEnvironment.Version == oM.Python.Enums.PythonVersion.Undefined)
            {
                BH.Engine.Reflection.Compute.RecordError("The environment is not valid as it does not contain either a name or version.");
                return "";
            }
            return $"Environment: {pythonEnvironment.Name}\nVersion: {pythonEnvironment.Version}\nLocation: {Query.EnvironmentDirectory(pythonEnvironment)}";
        }
    }
}
