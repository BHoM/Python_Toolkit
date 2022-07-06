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

using BH.oM.Python;
using BH.oM.Base.Attributes;

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Run a string containing Python code and return the output.")]
        [Input("env", "The Python environment with which to run the Python script.")]
        [Input("pythonString", "The string containing the Python script.")]
        [Output("result", "The stdout data from the executed Python script.")]
        public static string RunPythonString(this PythonEnvironment env, string pythonString)
        {
            if (!pythonString.Contains("print"))
            {
                BH.Engine.Base.Compute.RecordWarning("Nothing is being passed to StdOut in the Python script, so nothing will be returned from this method.");
            }

            // place pythonScript into a temporary .py file to reference and run, then call using the passed environment
            string scriptFile = Path.Combine(Path.GetTempPath(), "_BHoM_PythonScript.py");
            using (StreamWriter outputFile = new StreamWriter(scriptFile))
            {
                outputFile.WriteLine(pythonString);
            }

            string cmd = $"{env.Executable} {scriptFile}";

            return RunCommandStdout(cmd, hideWindows: true);
        }
    }
}

