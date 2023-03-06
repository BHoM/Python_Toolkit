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
        [Description("Install a virtualenv of the given configuration.")]
        [Input("name", "The name of this virtualenv.")]
        [Input("pythonVersion", "The version of Python to use for this environment.")]
        [Input("localPackage", "A local package to be included in the resultant virtualenv. This is where custom BHoM code can be added into this environment.")]
        [Input("run", "Run the installation process for this virtualenv.")]
        [Output("env", "The exectuble for the resultant virtualenv.")]
        public static oM.Python.PythonEnvironment InstallVirtualenv(
            string name,
            oM.Python.Enums.PythonVersion pythonVersion, 
            string localPackage = null, 
            bool run = false
        )
        {

            if (!IsValidEnvironmentName(name))
            {
                BH.Engine.Base.Compute.RecordError("A BHoM Python environment cannot cannot contain invalid filepath characters.");
                return null;
            }

            if (!run)
            {
                BH.Engine.Base.Compute.RecordWarning($"Please toggle \"{nameof(run)}\" to true.");
                return null;
            }

            // check to see if environment already exists and return it if it does!
            PythonEnvironment existingEnv = Query.ExistingEnvironment(name);
            if (existingEnv != null)
            {
                BH.Engine.Base.Compute.RecordNote($"A Python environment with the name \"{name}\" already exists and is being returned here. To reinstall this environment, delete the {Path.Combine(Query.EnvironmentDirectory(), name)} directory and re-run this method.");
                return existingEnv;
            }
            BH.Engine.Base.Compute.ClearCurrentEvents();

            // check to see if the base BHoM Python environment is installed and install it if it's not
            PythonEnvironment baseEnv = Query.ExistingEnvironment(Query.ToolkitName());
            if (baseEnv == null)
            {
                baseEnv = Compute.InstallBasePythonEnvironment(run);
            }
            BH.Engine.Base.Compute.ClearCurrentEvents();

            // set location where virtual env will be created
            string targetDirectory = Query.EnvironmentDirectory(name);
            if (targetDirectory is null)
            {
                targetDirectory = Path.Combine(Query.EnvironmentDirectory(), name);
                Directory.CreateDirectory(targetDirectory);
            }

            // get the python version executable to reference for this virtualenv
            string executable = pythonVersion.DownloadPython();

            // create log of installation as process continues - useful for debugging if things go wrong!
            string logFile = Path.Combine(targetDirectory, "installation.log");

            // create installation commands
            string baseBHoMPackage = Path.Combine(Query.CodeDirectory(), baseEnv.Name);
            List<string> installationCommands = new List<string>() {
                $"{baseEnv.Executable} -m virtualenv --python={executable} {targetDirectory}",  // create the virtualenv of the target executable
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m pip install ipykernel pytest",  // install ipykernel and pytest into virtualenv
                $"{Path.Combine(targetDirectory, "Scripts", "activate")} && python -m ipykernel install --name={name}",  // register environment with ipykernel
            };

            using (StreamWriter sw = File.AppendText(logFile))
            {
                sw.WriteLine(LoggingHeader($"Installation started for standalone {name} Python environment"));
                sw.Flush();

                foreach (string command in installationCommands)
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] {command}");
                    sw.Flush();
                    sw.WriteLine(Compute.RunCommandStdout($"{command}", hideWindows: true));
                    sw.Flush();
                }
             
                if (localPackage != null)
                {
                    sw.WriteLine($"[{System.DateTime.Now.ToString("s")}] Installing local package - {localPackage}");
                    sw.Flush();
                    sw.WriteLine(Query.ExistingEnvironment(name).InstallLocalPackage(localPackage));
                    sw.Flush();
                }
            }

            // query the newly created environment and return it
            return Query.ExistingEnvironment(name);
        }
    }
}

