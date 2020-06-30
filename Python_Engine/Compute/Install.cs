/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2020, the respective contributors. All rights reserved.
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

using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using Python.Runtime;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static async Task Install(bool force = false)
        {
            if (Runtime.pyversion != "3.7")
                throw new InvalidOperationException("You must compile Python.Runtime with PYTHON37 flag! Runtime version: " + Runtime.pyversion);

            string home = Query.EmbeddedPythonHome();
            string path = Environment.GetEnvironmentVariable("PATH", EnvironmentVariableTarget.User);
            if (!path.Contains(home))
                Environment.SetEnvironmentVariable("PATH", path + ";" + home, EnvironmentVariableTarget.User);

            // make sure pyBHoM is imported at python startup
            string startupCommand = "import pyBHoM";
            string pythonStartup = Environment.GetEnvironmentVariable("PYTHONSTARTUP", EnvironmentVariableTarget.User);
            pythonStartup = null;
            // if no startup file is defined, write one
            if (pythonStartup == null)
            {
                pythonStartup = Path.Combine(home, "startup.py");
                Directory.CreateDirectory(home);
                System.IO.File.WriteAllText(pythonStartup, startupCommand);
                Environment.SetEnvironmentVariable("PYTHONSTARTUP", pythonStartup, EnvironmentVariableTarget.User);
            }
            // if it exists, and does not contain the pyBHoM command already, append it
            else if (!File.ReadAllLines(pythonStartup).Contains(startupCommand))
            {
                using (StreamWriter file = new StreamWriter(pythonStartup, true))
                    file.WriteLine(startupCommand);
            }

            if (!force && Query.IsInstalled()) // python seems installed, so exit
                return;

            if (!Directory.Exists(Query.EmbeddedPythonHome()))
                Directory.CreateDirectory(Query.EmbeddedPythonHome());

            await Task.Run(() =>
            {
                string resourceName = typeof(Compute).Assembly.GetManifestResourceNames().FirstOrDefault(x => x.Contains(EMBEDDED_PYTHON));
                if (resourceName == null)
                    throw new FileNotFoundException($"No embedded python zip resource found for {resourceName}");

                // Copy the python embedded zip file to AppData/Roaming/BHoM/
                string targetFolder = Query.EmbeddedPythonHome();
                string targetPath = targetFolder + ".zip";
                CopyEmbeddedResourceToFile(resourceName, targetPath, force);

                try
                {
                    ZipFile.ExtractToDirectory(targetPath, targetPath.Replace(".zip", ""));

                    // allow pip on embedded python installation by unflagging python as embedded
                    // see https://github.com/pypa/pip/issues/4207#issuecomment-281236055
                    File.Delete(Path.Combine(Query.EmbeddedPythonHome(), PYTHON_VERSION + "._pth"));

                }
                catch
                {
                }
                finally
                {
                    // Clean up
                    if (File.Exists(targetPath))
                        File.Delete(targetPath);
                }
            });
        }


        /***************************************************/
        /**** Public Fields                             ****/
        /***************************************************/

        public const string EMBEDDED_PYTHON = "python-3.7.3-embed-amd64";

        public const string PYTHON_VERSION = "python37";

        /***************************************************/
    }
}
