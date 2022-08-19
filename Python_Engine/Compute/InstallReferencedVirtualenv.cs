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

using BH.oM.Base.Attributes;
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
                BH.Engine.Base.Compute.RecordError($"{executable} doesn't exist.");
                return null;
            }

            if (!run)
            {
                BH.Engine.Base.Compute.RecordWarning($"Please toggle `{nameof(run)}` to true.");
                return null;
            }

            // install base BHoM Python environment if it's not already installed
            oM.Python.PythonEnvironment baseEnv = Compute.InstallBasePythonEnvironment(run);
            string bhomPythonExecutable = baseEnv.Executable;

            // set location where virtual env will be created
            string targetDirectory = Path.Combine(Query.EnvironmentsDirectory(), name);
            if (!Directory.Exists(targetDirectory))
                Directory.CreateDirectory(targetDirectory);

            // return existing env if it already exists
            oM.Python.PythonEnvironment env = new oM.Python.PythonEnvironment() { Name = name, Executable = Path.Combine(targetDirectory, "Scripts", "python.exe") };
            if (env.EnvironmentExists())
                return env;

            // create paths for use in this process
            executable = Modify.AddQuotesIfRequired(executable);

            // create log of installation as process continues - useful for debugging if things go wrong!
            string logFile = Path.Combine(targetDirectory, "installation.log");

            // create installation commands
            List<string> installationCommands = new List<string>() {
                $"{bhomPythonExecutable} -m virtualenv --python={executable} {targetDirectory}",  // create the virtualenv of the target executable
                $"{executable} -m pip freeze > {Path.Combine(targetDirectory, "requirements.txt")}",  // get the installed packages from the referenced executable
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m pip install -r {Path.Combine(targetDirectory, "requirements.txt")}",  // install requirements into virtualenv
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m pip install ipykernel",  // install ipykernel into virtualenv
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m pip install pytest",  // install pytest into virtualenv
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m ipykernel install --name={name}",  // register environment with ipykernel
            };
            if (localPackage != null)
                installationCommands.Add($"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m pip install -e {Modify.AddQuotesIfRequired(localPackage)}");  // install local package into virtualenv

            using (StreamWriter sw = File.AppendText(logFile))
            {
                sw.WriteLine(LoggingHeader($"Installation started for referenced {name} Python environment"));

                foreach (string command in installationCommands)
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {command}");
                    sw.WriteLine(Compute.RunCommandStdout($"{command}", hideWindows: true));
                }
            }

            return env;
        }
    }
}
