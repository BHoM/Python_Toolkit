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
using BH.oM.Reflection.Attributes;

using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Return the Python executable for the given BHoM Python environment.")]
        [Input("pythonEnvironment", "A BHoM Python environment object.")]
        [Output("pythonExecutable", "The executable associated with the given BHoM Python environment.")]
        public static string PythonExecutable(this PythonEnvironment pythonEnvironment)
        {
            string environmentDirectory = Query.EnvironmentDirectory(pythonEnvironment);
            if (!Directory.Exists(environmentDirectory))
            {
                return null;
            }
            string[] files = Directory.GetFiles(environmentDirectory, "python.exe", SearchOption.AllDirectories);
            if (files.Length == 1)
            {
                return files[0];
            }
            else if (files.Length > 1)
            {
                BH.Engine.Reflection.Compute.RecordError($"More than one Python executable was found in {environmentDirectory}!");
                return files[0];
            }
            else
            {
                BH.Engine.Reflection.Compute.RecordError($"No Python executable was found in {environmentDirectory}.");
                return null;
            }
        }
    }
}


