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

using BH.oM.Python.Enums;
using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.ComponentModel;
using System.IO;
using System.Linq;
using System;
using System.Collections.Generic;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Check whether a named BHoM Python virtual environment exists.")]
        [Input("envName", "The name given to the BHoM Python Environment.")]
        [Input("pythonVersion", "The version to check against.")]
        [Output("exists", "True if exists, False if not.")]
        [PreviousVersion("7.0", "BH.Engine.Python.Query.VirtualEnvironmentExists(System.String)")]
        public static bool VirtualEnvironmentExists(string envName, PythonVersion pythonVersion = PythonVersion.Undefined)
        {
            bool directoryExists = Directory.Exists(VirtualEnvironmentDirectory(envName));
            bool executableExists = File.Exists(VirtualEnvironmentExecutable(envName));
            bool kernelExists = Directory.Exists(VirtualEnvironmentKernel(envName));
            bool versionMatches = Version(VirtualEnvironmentExecutable(envName)) == pythonVersion;

            if (pythonVersion == PythonVersion.Undefined)
                return directoryExists && executableExists && kernelExists;
            
            return directoryExists && executableExists && kernelExists && versionMatches;
        }

        [Description("Get the path to the named BHoM Python virtual environment kernel.")]
        [Input("envName", "The name given to the BHoM Python Environment.")]
        [Output("kernelDirectory", "The path to the kernel directory.")]
        public static string VirtualEnvironmentKernel(string envName)
        {
            return Path.Combine(Query.DirectoryKernels(), envName);
        }

        [Description("Get the path to the named BHoM Python virtual environment executable.")]
        [Input("envName", "The name given to the BHoM Python Environment.")]
        [Output("executable", "The path to the executable.")]
        public static string VirtualEnvironmentExecutable(string envName)
        {
            return Path.Combine(Query.DirectoryEnvironments(), envName, "Scripts", "python.exe");
        }

        [Description("Get the path to the named BHoM Python virtual environment.")]
        [Input("envName", "The name given to the BHoM Python Environment.")]
        [Output("directory", "The directory where the virtual environment is located.")]
        public static string VirtualEnvironmentDirectory(string envName)
        {
            return Path.Combine(Query.DirectoryEnvironments(), envName);
        }

        [Description("Get the named BHoM Python virtual environment.")]
        [Input("envName", "The name given to the BHoM Python Environment.")]
        [Output("environment", "The BHoM Python Environment.")]
        public static PythonEnvironment VirtualEnvironment(string envName)
        {
            if (!VirtualEnvironmentExists(envName))
                return null;
            
            return new PythonEnvironment()
            {
                Name = envName,
                Executable = VirtualEnvironmentExecutable(envName),
            };
        }
    }
}

