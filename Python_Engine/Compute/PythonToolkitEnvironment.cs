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

using BH.oM.Base.Attributes;

using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install/query the Python_Toolkit BHoM Python Environment.")]
        [Input("run", "Run the installation process for the BHoM Python Environment.")]
        [Input("force", "Force reinstallation of this BHoM Python Environment.")]
        [Output("env", "A BHoM Python Environment.")]
        public static oM.Python.PythonEnvironment PythonToolkitEnvironment(bool run = false, bool force = false)
        {
            string toolkitName = Query.ToolkitName();
            string toolkitEnvironmentDirectory = Path.Combine(Query.EnvironmentsDirectory(), toolkitName);

            if (run)
            {
                if (Query.EnvironmentExists(toolkitName) && !force)
                {
                    return new oM.Python.PythonEnvironment()
                    {
                        Name = Query.ToolkitName(),
                        Executable = Path.Combine(Query.EnvironmentsDirectory(), toolkitName, "python.exe"),
                    };
                }

                if (Query.EnvironmentExists(toolkitName) && force)
                    Compute.DeleteDirectory(toolkitEnvironmentDirectory);

                return Compute.InstallPythonEnvironment(
                    version: oM.Python.Enums.PythonVersion.v3_10_5,
                    name: toolkitName,
                    additionalPackage: Path.Combine(Query.CodeDirectory(), toolkitName)
                );
            }
            return null;
        }
    }
}
