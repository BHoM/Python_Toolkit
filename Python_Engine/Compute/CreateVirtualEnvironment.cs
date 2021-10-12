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

using BH.oM.Reflection;
using BH.oM.Reflection.Attributes;
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

        [Description("Create a virtual Python environment.")]
        [Input("name", "The name of the environment to be created.")]
        [Input("directory", "The directory in which the environment should be created.")]
        [Input("packages", "A list of packages, in the usual Pip format (if a version is included, it should be written as \"package_name==0.0.0\"). If no version is given, then the most recent version available will be used.")]
        [Input("run", "Set to True to create the environment.")]
        [MultiOutput(0, "success", "True if environment creation is successful, false if otherwise.")]
        [MultiOutput(1, "executable", "The path to the environments Python executable.")]
        public static Output<bool, string> CreateVirtualEnvironment(string name, List<string> packages = null, bool run = false)
        {
            string envsDir = Directory.CreateDirectory(Path.Combine(Query.EmbeddedPythonHome(), "envs")).FullName;

            // Construct the paths used herein
            string environmentPath = Path.Combine(envsDir, name);
            string envPythonExecutable = Path.Combine(environmentPath, "Scripts", "python.exe");
            string basePythonExecutable = Path.Combine(Python.Query.EmbeddedPythonHome(), "python.exe");

            if (Directory.Exists(environmentPath))
            {
                BH.Engine.Reflection.Compute.RecordWarning($"An environment called \"{name}\" already exists. If you run this method it will be overwritten!");
            }

            if (run)
            {
                // remove the old version of this environment (if it exists)
                if (Directory.Exists(environmentPath))
                {
                    Directory.Delete(environmentPath, true);
                }

                // create the new environment
                RunCommand(command: $"{basePythonExecutable} -m virtualenv \"{environmentPath}\"");

                // Install ipykernel and requested packages new environment
                if (packages == null)
                {
                    packages = new List<string>();
                }
                Compute.PipInstall(envPythonExecutable, packages, false, "", true);

                // Create a requirements.txt file to record this environments setup.
                string requirements = Path.Combine(environmentPath, "requirements.txt");
                RunCommand($"{envPythonExecutable} -m pip freeze > {requirements}");

                return new Output<bool, string>() { Item1 = true, Item2 = envPythonExecutable };
            }
            return new Output<bool, string>() { Item1 = false, Item2 = "" };
        }

        /***************************************************/

    }
}
