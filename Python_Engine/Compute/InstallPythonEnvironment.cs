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

using BH.oM.Python;
using BH.oM.Reflection.Attributes;

using System.Collections.Generic;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install the default BHoM Python_Toolkit environment.")]
        [Input("run", "Set to True to run the PythonEnvironment installer.")]
        [Input("force", "If the environment already exists recreate it rather than re-using it.")]
        [Output("pythonEnvironment", "The default BHoM Python_Toolkit environment object.")]
        public static PythonEnvironment InstallPythonEnvironment(bool run = false, bool force = false)
        {
            oM.Python.Enums.PythonVersion version = oM.Python.Enums.PythonVersion.v3_9_7;

            List<PythonPackage> packages = new List<PythonPackage>()
            {
                new PythonPackage(){ Name="pandas", Version="1.3.4" },
                new PythonPackage(){ Name="numpy", Version="1.21.3" },
                new PythonPackage(){ Name="matplotlib", Version="3.4.3" },
                new PythonPackage(){ Name="pymongo", Version="3.12.1" },
                new PythonPackage(){ Name="SQLAlchemy", Version="1.4.27" },
                new PythonPackage(){ Name="pyodbc", Version="4.0.32" },
            };

            PythonEnvironment pythonEnvironment = Create.PythonEnvironment(Query.ToolkitName(), version, packages);

            return Python.Compute.InstallToolkitPythonEnvironment(pythonEnvironment, force, run);
        }
    }
}
