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

using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get the path to the named Python virtual environment executable.")]
        [Input("name", "The name given to the Python Environment.")]
        [Output("executable", "The path to the executable.")]
        public static string VirtualEnvironmentExecutable(string name)
        {   
            string exePath = Path.Combine(Query.DirectoryEnvironments(), name, "venv", "Scripts", "python.exe");
            if (!File.Exists(exePath))
                Base.Compute.RecordError($"{exePath} was not found.");

            return exePath;
        }

        [Description("Check whether a named Python virtual environment exists.")]
        [Input("name", "The name given to the Python Environment.")]
        [Output("exists", "True if exists, False if not.")]
        public static bool VirtualEnvironmentExists(string name)
        {
            string expectedVenvPath = Path.Combine(Query.DirectoryEnvironments(), name, "venv");
            
            if (Directory.Exists(expectedVenvPath) & File.Exists(VirtualEnvironmentExecutable(name)))
                return true;
                
            return false;
        }

        [Description("Get the named Python virtual environment.")]
        [Input("name", "The name given to the Python Environment.")]
        [Output("environment", "The Python Environment.")]
        public static PythonEnvironment VirtualEnvironment(string name)
        {
            if (!VirtualEnvironmentExists(name))
                Base.Compute.RecordError($"{name} was not found in {Query.DirectoryEnvironments()}");

            return new PythonEnvironment()
            {
                Name = name,
                Executable = VirtualEnvironmentExecutable(name),
            };
        }

        [Description("Get a named Python virtual environment.")]
        [Input("name", "The name given to the Python Environment.")]
        [Output("directory", "The directory in which the venv resides.")]
        public static string VirtualEnvironmentDirectory(string name)
        {
            if (!VirtualEnvironmentExists(name))
                Base.Compute.RecordError($"{name} was not found in {Query.DirectoryEnvironments()}");

            return Path.Combine(Query.DirectoryEnvironments(), name);
        }
    }
}
