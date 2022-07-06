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
using BH.oM.Base.Attributes;

using System.ComponentModel;
using System.IO;
using System.Linq;
using System;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Check whether a named BHoM Python Environment already exists.")]
        [Input("name", "The name of the BHoM Python Environment.")]
        [Output("exists", "True if the environment already exists, False if not.")]
        public static bool EnvironmentExists(string name)
        {
            if (Directory.Exists(Path.Combine(Query.EnvironmentsDirectory(), name)) && File.Exists(Path.Combine(Query.EnvironmentsDirectory(), name, "python.exe")))
            {
                return true;
            }
            return false;
        }

        [Description("Check whether a BHoM Python Environment already exists.")]
        [Input("env", "The BHoM Python Environment.")]
        [Output("exists", "True if the environment already exists, False if not.")]
        public static bool EnvironmentExists(this oM.Python.PythonEnvironment env)
        {
            if (Directory.Exists(Path.Combine(Query.EnvironmentsDirectory(), env.Name)) && File.Exists(env.Executable))
            {
                return true;
            }
            return false;
        }
    }
}
