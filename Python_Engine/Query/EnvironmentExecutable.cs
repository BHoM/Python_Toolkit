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

using System.ComponentModel;
using System.IO;
using System.Xml.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("The location where `python.exe` for a named BHoM Python environment would reside. This method returns null if the named environment does not exist.")]
        [Input("envName", "The virtual environment name.")]
        [Output("The location where a Python virtual environment would reside.")]
        public static string EnvironmentExecutable(string envName)
        {
            string exePath;
            if (envName == "Python_Toolkit")
            {
                exePath = Path.Combine(EnvironmentDirectory(envName), "python.exe");
            }
            else
            {
                exePath = Path.Combine(EnvironmentDirectory(envName), "Scripts", "python.exe");
            }

            if (File.Exists(exePath))
            {
                return exePath;
            }
            return null;
        }
    }
}


