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
using System.Xml.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get an installed environment without the overhead of attempting to install that environment.")]
        [Input("envName","The virtual environment name to request.")]
        [Output("The virtual environment, if it exists.")]
        public static PythonEnvironment VirtualEnv(string envName)
        {
            string exePath = Query.VirtualEnvPythonExePath(envName);
            if (File.Exists(exePath))
            {
                return new PythonEnvironment() { Name = envName, Executable = exePath };
            }
            else
            {
                BH.Engine.Base.Compute.RecordError($"No environment could be found for {envName}. Use the appropriate InstallPythonEnv to install this environment.");
                return null;
            }
        }
    }
}


