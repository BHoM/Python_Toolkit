/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
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
    public static partial class Compute
    {
        [Description("Remove the named Python virtual environment.")]
        [Input("name", "The name of the Python virtual environment to remove.")]
        [Input("run", "Run this method.")]
        public static void RemoveVirtualEnvironment(string name, bool run = false)
        {
            if (!Query.VirtualEnvironmentExists(name))
            {
                Base.Compute.RecordError($"No Python environment named {name} exists.");
                return;
            }

            string venvDirectory = Path.Combine(Query.DirectoryEnvironments(), name);

            if (run)
            {
                RemoveKernel(name, run);

                try 
                {
                    Directory.Delete(venvDirectory, true);
                }
                catch (IOException ex)
                {
                    Base.Compute.RecordError($"Failed to remove virtual environment directory {venvDirectory}: {ex.Message}");
                }
            }
        }

        [Description("Remove the named Jupyter kernel.")]
        [Input("name", "The name of the Jupyer kernel to remove.")]
        [Input("run", "Run this method.")]
        public static void RemoveKernel(string name, bool run = false)
        {
            if (!Query.VirtualEnvironmentExists(name))
            { 
                Base.Compute.RecordError($"No Python environment named {name} exists.");
                return;
            }

            PythonEnvironment venv = Query.VirtualEnvironment(name);
            string cmd = $"{venv.Executable} -m jupyter kernelspec uninstall {name} -f";

            if (run)
            {
                RunCommandStdout(command: cmd, hideWindows: true);
            }
            else
            {
                Base.Compute.RecordNote($"The following command will be executed: {cmd}");
            }
        }
    }
}
