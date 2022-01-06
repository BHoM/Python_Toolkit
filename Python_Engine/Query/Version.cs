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
using BH.oM.Reflection.Attributes;

using System.ComponentModel;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Return the Python version of the current BHoM Python environment.")]
        [Input("pythonEnvironment", "A BHoM Python environment.")]
        [Output("version", "The version of Python installed in the given Python environment.")]
        public static PythonVersion Version(this PythonEnvironment pythonEnvironment)
        {
            string command = $"{pythonEnvironment.PythonExecutable()} --version";
            string output = Compute.RunCommandStdout(command, hideWindows: true);
            if (output.StartsWith("'--version"))
            {
                return PythonVersion.Undefined;
            }
            else
            {
                string versionString = $"v{output.Split(' ').Last().Trim().Replace(".", "_")}";
                return (PythonVersion)System.Enum.Parse(typeof(PythonVersion), versionString);
            }
        }
    }
}

