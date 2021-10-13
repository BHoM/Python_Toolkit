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

using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Return True if the named package is installed in the base BHoM Python environment.")]
        public static bool IsModuleInstalled(this string module)
        {
            if (!IsPythonInstalled())
                return false;

            module = module.Split('.')[0];

            string packagesDir = Path.Combine(Query.EmbeddedPythonHome(), "Lib", "site-packages");
            string moduleDir = Path.Combine(packagesDir, module);
            bool installed = Directory.Exists(moduleDir) && File.Exists(Path.Combine(moduleDir, "__init__.py"));
            installed |= File.Exists(Path.Combine(packagesDir, module.Split('_')[0] + "-Toolkit.egg-link"));
            return installed;
        }

        /***************************************************/
    }
}

