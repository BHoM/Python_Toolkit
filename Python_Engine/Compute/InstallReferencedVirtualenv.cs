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
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install the Python Environment into BHoM for a referenced existing Python environment.")]
        [Input("name", "The name of this BHoM Python Environment.")]
        [Input("executable", "The Python executable for the referenced environment. From this, the version of Python will be determined in order to recreate it for BHoM as a virtualenv.")]
        [Input("localPackage", "A local package to be included in the resultant environment. This is where custom BHoM code can be added into this environment.")]
        [Input("run", "Run the installation process for the BHoM Python Environment.")]
        [Output("env", "The virtualenv replication of  Python Environment for BHoM workflows.")]
        public static oM.Python.PythonEnvironment InstallReferencedVirtualenv(
            string name,
            string executable, 
            string localPackage = null, 
            bool run = false
        )
        {
            if (!IsValidEnvironmentName(name))
            {
                BH.Engine.Base.Compute.RecordError("A BHoM Python virtualenv cannot cannot contain invalid filepath characters.");
                return null;
            }

            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError($"{executable} doesn't exist so an environment cannot be created based on it.");
                return null;
            }

            if (!run)
            {
                BH.Engine.Base.Compute.RecordWarning($"Please toggle \"{nameof(run)}\" to true.");
                return null;
            }

            // install base BHoM Python environment if it's not already installed
            oM.Python.PythonEnvironment baseEnv = Compute.InstallBasePythonEnvironment(run);
            string bhomPythonExecutable = baseEnv.Executable;

            // set location where virtual env will be created
            string targetDirectory = Query.EnvironmentDirectory(name);
            if (targetDirectory is null)
            {
                targetDirectory = Path.Combine(Query.EnvironmentDirectory(), name);
                Directory.CreateDirectory(targetDirectory);
            }
            string logFile = Path.Combine(targetDirectory, "installation.log");

            // get the version of python from the passed executable
            string versionString = Compute.RunCommandStdout($"\"{executable}\" --version").Replace("Python ", "");
            BH.oM.Python.Enums.PythonVersion version = Query.PythonVersion(versionString);

            // run the virtualenv install process
            PythonEnvironment env = Compute.InstallVirtualenv(name=name, version=version, localPackage=null, run=run);

            // install matching packages from the referenced environment
            using (StreamWriter sw = File.AppendText(logFile))
            {
                // get requirements.txt file from existgin enviromnment
                string requirementsTxtFile = Path.Combine(targetDirectory, "requirements.txt");
                string requirementsTxtCommand = $"{Modify.AddQuotesIfRequired(executable)} -m pip freeze > {requirementsTxtFile}";
                sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {requirementsTxtCommand}");
                sw.Flush();
                sw.WriteLine(Compute.RunCommandStdout(requirementsTxtCommand));
                sw.Flush();

                string requirementsInstallCommand = $"{Modify.AddQuotesIfRequired(env.Executable)} -m pip install -r {requirementsTxtFile}";
                sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {requirementsInstallCommand}");
                sw.Flush();
                sw.WriteLine(Compute.RunCommandStdout(requirementsInstallCommand));
                sw.Flush();
            }

            // install local package if it's been passed
            if (localPackage != null)
            {
                using (StreamWriter sw = File.AppendText(logFile))
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] Installing local package - {localPackage}");
                    sw.Flush();
                    sw.WriteLine(env.InstallLocalPackage(localPackage));
                    sw.Flush();
                }
            }

           return env;
        }
    }
}

