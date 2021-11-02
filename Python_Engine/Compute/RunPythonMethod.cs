///*
// * This file is part of the Buildings and Habitats object Model (BHoM)
// * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
// *
// * Each contributor holds copyright over their respective contributions.
// * The project versioning (Git) records all such contribution source information.
// *                                           
// *                                                                              
// * The BHoM is free software: you can redistribute it and/or modify         
// * it under the terms of the GNU Lesser General Public License as published by  
// * the Free Software Foundation, either version 3.0 of the License, or          
// * (at your option) any later version.                                          
// *                                                                              
// * The BHoM is distributed in the hope that it will be useful,              
// * but WITHOUT ANY WARRANTY; without even the implied warranty of               
// * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
// * GNU Lesser General Public License for more details.                          
// *                                                                            
// * You should have received a copy of the GNU Lesser General Public License     
// * along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
// */

using BH.oM.Base;
using BH.oM.Python;
using BH.oM.Reflection.Attributes;

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Run a BHoM Python method and return the output as a custom object.")]
        [Input("pythonEnvironment", "The Python environment with which to run the Python script.")]
        [Input("method", "The Python method to be called.")]
        [Input("arguments", "A list of named arguments (all callable BHoM Python code should include these as argparse attributes.")]
        [Input("values", "Corresponding values for each argument passed.")]
        [Output("obj", "The resultant BHoM CustomObject.")]
        public static CustomObject RunPythonMethod(PythonEnvironment pythonEnvironment, string method, List<string> arguments = null, List<string> values = null)
        {
            if (arguments.Count != values.Count)
            {
                BH.Engine.Reflection.Compute.RecordError("arguments and values must be the same length.");
                return null;
            }

            string pythonExecutable = pythonEnvironment.PythonExecutable();
            if (pythonExecutable is null)
            {
                return null;
            }

            string pythonScript = Path.Combine(pythonEnvironment.CodeDirectory(), $"{method}.py");
            if (!File.Exists(pythonScript))
            {
                BH.Engine.Reflection.Compute.RecordError($"{method}.py does not exist in {pythonEnvironment.CodeDirectory()}.");
                return null;
            }

            string cmd = $"{pythonExecutable} {pythonScript}";
            if (arguments.Count > 0)
            {
                for (int i = 0; i < arguments.Count; i++)
                {
                    cmd += $" {arguments[i]} {values[i]}";
                }
            }

            string tempFile = RunCommandStdout(cmd, hideWindows: true).Trim();

            return Serialiser.Convert.FromJson(File.ReadAllText(tempFile)) as CustomObject;
        }
    }
}
