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

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install the default BHoM Python_Toolkit environment.")]
        [Input("run", "Set to True to run the PythonEnvironment installer.")]
        [Input("force", "If the environment already exists recreate it rather than re-using it.")]
        [Input("configJSON", "Path to a config JSON containing Python environment configuration.")]
        [Output("pythonEnvironment", "The default BHoM Python_Toolkit environment object.")]
        public static PythonEnvironment InstallPythonEnvironment(bool run = false, bool force = false, string configJSON = @"C:\ProgramData\BHoM\Settings\Python\Python_Toolkit.json")
        {
            PythonEnvironment pythonEnvironment = Create.PythonEnvironment(configJSON);

            return pythonEnvironment.InstallToolkitPythonEnvironment(force, run);
        }
    }
}

