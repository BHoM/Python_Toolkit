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

namespace BH.Engine.Python
{
    public static partial class Create
    {
        [Description("Create a BHoM Python Environment from an existing Python executable.")]
        [Input("name", "The name of the Python Environment.")]
        [Input("executable", "The path to the executable for this Python Environment.")]
        [Input("codeDirectory", "The path to the custom BHoM code for this Python Environment.")]
        [Output("environment", "A BHoM Python Environment object.")]
        public static BH.oM.Python._Environment Environment(string name, string executable, string codeDirectory = null)
        {
            if (!BH.Engine.Python.Query.ValidEnvironmentName(name))
                return null;

            if (!System.IO.File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError($"{executable} does not exist.");
                return null;
            }

            if (!System.IO.Directory.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError($"{codeDirectory} does not exist.");
                return null;
            }
            else if (!System.IO.File.Exists(System.IO.Path.Combine(codeDirectory, "__init__.py")))
            {
                BH.Engine.Base.Compute.RecordWarning($"{System.IO.Path.Combine(codeDirectory, "__init__.py")} does not exist and some functionality using this environments \"codeDirectory\" will not be possible.");
            }

            return new BH.oM.Python._Environment()
            {
                Name = name,
                Executable = executable,
                CodeDirectory = codeDirectory,
            };
        }

        [Description("Create a BHoM Python Environment from a given Python version and optional \"requirements.txt\" file.")]
        [Input("name", "The name of the Python Environment.")]
        [Input("version", "The version of Python to use for this Python Environment.")]
        [Input("requirementsFile", "The path to the \"requirements.txt\" to install in this Python Environment.")]
        [Input("codeDirectory", "The path to the custom BHoM code for this Python Environment.")]
        [Output("environment", "A BHoM Python Environment object.")]
        public static BH.oM.Python._Environment Environment(string name, PythonVersion version, string requirementsFile = null, string codeDirectory = null)
        {
            if (name.Any(x => Char.IsWhiteSpace(x)))
            {
                BH.Engine.Base.Compute.RecordError($"A BHoM Python Environment name cannot contain whitespace characters.");
                return null;
            }

            if (requirementsFile != null && !System.IO.File.Exists(requirementsFile))
            {
                BH.Engine.Base.Compute.RecordError($"{requirementsFile} does not exist.");
                return null;
            }

            // check if environment already exists in the default BHoM location
                // check if the environment that exists  matches the one proposed here (use a string comparison from the output of the queried env to match the requirement.txt proposed, or just the version string of Python if no requirements given)

            // install the environment


            return new BH.oM.Python._Environment()
            {
                Name = name,
                Executable = executable,
                CodeDirectory = codeDirectory,
            };
        }



        //[Description("Create a BHoM Python environment from an environment.json config file.")]
        //[Input("configJSON", "The path to the environment.json config file.")]
        //[Output("pythonEnvironment", "A BHoM PythonEnvironment object.")]
        //public static PythonEnvironment PythonEnvironment(string configJSON)
        //{
        //    string environmentName = System.IO.Path.GetFileNameWithoutExtension(configJSON);

        //    // load the json
        //    string jsonStr = System.IO.File.ReadAllText(configJSON);
        //    BH.oM.Base.CustomObject obj = (BH.oM.Base.CustomObject)BH.Engine.Serialiser.Convert.FromJson(jsonStr);

        //    string versionString = (string)BH.Engine.Base.Query.PropertyValue(obj.CustomData, "Version");
        //    PythonVersion environmentVersion = (PythonVersion)Enum.Parse(typeof(PythonVersion), $"v{versionString.Replace(".", "_")}");

        //    List<object> pkgObjects = (List<object>)BH.Engine.Base.Query.PropertyValue(obj.CustomData, "Packages");
        //    List<PythonPackage> environmentPackages = new List<PythonPackage>();
        //    foreach (object pkgObject in pkgObjects)
        //    {
        //        string pkgName = (string)BH.Engine.Base.Query.PropertyValue((BH.oM.Base.CustomObject)pkgObject, "Name");
        //        string pkgVersion = (string)BH.Engine.Base.Query.PropertyValue((BH.oM.Base.CustomObject)pkgObject, "Version");
        //        environmentPackages.Add(
        //                new PythonPackage() { Name = pkgName, Version = pkgVersion }
        //            );
        //    }

        //    // populate the PythonEnvironment
        //    PythonEnvironment pythonEnvironment = new PythonEnvironment()
        //    {
        //        Name = environmentName,
        //        Version = environmentVersion,
        //        Packages = environmentPackages
        //    };

        //    return pythonEnvironment;
        //}
    }
}

