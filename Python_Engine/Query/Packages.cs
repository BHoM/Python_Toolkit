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
using System.Collections.Generic;
using System;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get the list of packages available for a given Python executable.")]
        [Input("executable", "The path to a Python executable.")]
        [Output("packages", "The packages available for the given Python executable.")]
        public static List<string> Packages(string executable)
        {
            if (!File.Exists(executable))
            {
                BH.Engine.Base.Compute.RecordError($"{executable} does not exist.");
                return null;
            }

            string tempPackageFile = Path.Combine(Path.GetTempPath(), $"{Guid.NewGuid()}.txt");
            string command = $"{executable} -m pip freeze > {tempPackageFile}";

            Compute.RunCommandBool(command, hideWindows: true);

            List<string> installedPackages = new List<string>(File.ReadAllLines(tempPackageFile));
            File.Delete(tempPackageFile);

            return installedPackages;
        }

        [Description("Get the list of packages available for a given Python environment.")]
        [Input("env", "A BHoM Python Environment.")]
        [Output("packages", "The packages available for the given BHoM Python Environment.")]
        public static List<string> Packages(this oM.Python.Environment env)
        {
            return Packages(env.Executable);
        }
    }
}
