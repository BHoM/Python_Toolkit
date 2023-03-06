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
using BH.oM.Python;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("The directory where all BHoM generated Python environments reside.")]
        [Output("The directory where all BHoM generated Python environments reside.")]
        public static string EnvironmentDirectory()
        {
            return Path.Combine(Query.ExtensionsDirectory(), "PythonEnvironments");
        }

        [Description("The directory where a named BHoM generated Python environment resides.")]
        [Input("envName", "The virtual environment name.")]
        [Output("The directory where a named BHoM generated Python environment resides. This method does returns null if that directory does not exist.")]
        public static string EnvironmentDirectory(string envName)
        {
            string directory = Path.Combine(EnvironmentDirectory(), envName);

            if (Directory.Exists(directory))
            {
                return directory;
            }

            return null;
        }

        [Description("The directory where this BHoM Python environment resides.")]
        [Input("env", "The environment stored within the requested directory.")]
        [Output("The directory where a named BHoM generated Python environment resides.")]
        public static string EnvironmentDirectory(this PythonEnvironment env)
        {
            return EnvironmentDirectory(env.Name);
        }
    }
}


