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
        [Description("Check whether a Python Environment already exists in the given location.")]
        [Input("directory", "The directory containing a named Python environment.")]
        [Input("directory", "The name of the Python environment (the subdirectory within \"directory\" that contains \"python.exe\").")]
        [Output("exists", "True if the environment exists, False if not.")]
        public static bool EnvironmentExists(string directory, string name)
        {
            string fullPath = Path.Combine(directory, name);
            if (Directory.Exists(fullPath) && File.Exists(Path.Combine(fullPath, "python.exe")))
                return true;

            return false;
        }
    }
}
