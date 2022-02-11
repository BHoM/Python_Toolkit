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

using BH.oM.Python.Enums;
using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System;
using BH.Adapter.File;

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Create a BHoM Python Environment, with additional checks to ensure that it is a valid object.")]
        [Input("name", "The name of the PythonEnvironment.")]
        [Input("version", "The version of Python to be used in this environment.")]
        [Input("packages", "A list of packages to be included in this Python environment.")]
        [Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        public static PythonEnvironment PythonEnvironment(string name, PythonVersion version, List<PythonPackage> packages = null)
        {
            if (name.Any(x => Char.IsWhiteSpace(x)))
            {
                BH.Engine.Base.Compute.RecordError($"A BHoM PythonEnvironment name cannot contain whitespace characters.");
                return null;
            }

            if (version == PythonVersion.Undefined)
            {
                BH.Engine.Base.Compute.RecordError($"The Python version chosen cannot be \"Undefined\".");
                return null;
            }

            return new PythonEnvironment()
            {
                Name = name,
                Version = version,
                Packages = packages,
            };
        }

        [Description("Create a BHoM Python environment from an environment.json config file.")]
        [Input("config", "The path to the environment.json config file.")]
        [Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        public static PythonEnvironment PythonEnvironment(string configJSON)
        {
            string environmentName = System.IO.Path.GetFileNameWithoutExtension(configJSON);

            // load the json
            string jsonStr = System.IO.File.ReadAllText(configJSON);
            BH.oM.Base.CustomObject obj = (BH.oM.Base.CustomObject)BH.Engine.Serialiser.Convert.FromJson(jsonStr);

            string versionString = (string)BH.Engine.Base.Query.PropertyValue(obj.CustomData, "Version");
            PythonVersion environmentVersion = (PythonVersion)Enum.Parse(typeof(PythonVersion), $"v{versionString.Replace(".", "_")}");

            List<object> pkgObjects = (List<object>)BH.Engine.Base.Query.PropertyValue(obj.CustomData, "Packages");
            List<PythonPackage> environmentPackages = new List<PythonPackage>();
            foreach (object pkgObject in pkgObjects)
            {
                string pkgName = (string)BH.Engine.Base.Query.PropertyValue((BH.oM.Base.CustomObject)pkgObject, "Name");
                string pkgVersion = (string)BH.Engine.Base.Query.PropertyValue((BH.oM.Base.CustomObject)pkgObject, "Version");
                environmentPackages.Add(
                        new PythonPackage() { Name = pkgName, Version = pkgVersion }
                    );
            }

            // populate the PythonEnvironment
            PythonEnvironment pythonEnvironment = new PythonEnvironment()
            {
                Name = environmentName,
                Version = environmentVersion,
                Packages = environmentPackages
            };

            return pythonEnvironment;
        }
    }
}

