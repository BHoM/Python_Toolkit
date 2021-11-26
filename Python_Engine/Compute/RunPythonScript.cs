/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
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

using BH.oM.Base;
using BH.oM.Python;
using BH.oM.Reflection.Attributes;

using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Run a Python script using the given BHoM PythonEnvironment, and return a BHoM object containing results.")]
        [Input("pythonEnvironment", "The Python environment with which to run the Python script.")]
        [Input("pythonScript", "A path to a Python script (a *.py file containing a __main__ executable function).")]
        [Input("arguments", "A list of optional arguments to pass to the script.")]
        [Output("obj", "A BHoM CustomObject containing results from this script.")]
        public static CustomObject RunPythonScript(this PythonEnvironment pythonEnvironment, string pythonScript, List<string> arguments = null)
        {
            string pythonExecutable = pythonEnvironment.PythonExecutable();
            if (pythonExecutable is null)
            {
                return null;
            }

            if (!File.Exists(pythonScript))
            {
                BH.Engine.Reflection.Compute.RecordError($"{pythonScript} does not exist.");
                return null;
            }

            string contents = File.ReadAllText(pythonScript);
            List<string> executableStrings = new List<string>()
            {
                "if __name__ == \"__main__\":",
                "if __name__ is \"__main__\":",
                "if __name__ == '__main__':",
                "if __name__ is '__main__':",
                "if __name__ == \'__main__\':",
                "if __name__ is \'__main__\':",
            };
            if (!executableStrings.Any(contents.Contains))
            {
                BH.Engine.Reflection.Compute.RecordError($"The script passed does not seem to be directly executable using Python. It should contain an 'if __name__ == \"__main__\"' to enable the file to be called directly.");
                return null;
            }

            string cmd = $"{pythonExecutable} {pythonScript}";
            if (arguments.Count > 0)
            {
                for (int i = 0; i < arguments.Count; i++)
                {
                    cmd += $" {arguments[i]}";
                }
            }

            string tempFile = RunCommandStdout(cmd, hideWindows: true);

            if (!File.Exists(tempFile))
            {
                if (arguments.Contains("-h"))
                {
                    BH.Engine.Reflection.Compute.RecordNote($"It looks like you've asked for some documentation. Here it is!");
                }
                else
                {
                    BH.Engine.Reflection.Compute.RecordError($"Something went wrong! The object returned contains the error message given by the Python code.");
                }
                
                return new CustomObject()
                {
                    CustomData = new Dictionary<string, object>()
                    {
                        { "output", (object)tempFile }
                    }
                };
            }
            else
            {
                string tempFileContent = File.ReadAllText(tempFile);
                return Serialiser.Convert.FromJson(tempFileContent) as CustomObject;
            }
        }
    }
}
