/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2020, the respective contributors. All rights reserved.
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

using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static bool IsPythonInstalled()
        {
            return File.Exists(Path.Combine(Query.EmbeddedPythonHome(), "python.exe"));

        }

        /***************************************************/

        public static bool IsPipInstalled()
        {
            return File.Exists(Path.Combine(Query.EmbeddedPythonHome(), "Scripts", "pip.exe"));
        }

        /***************************************************/

        public static bool IsModuleInstalled(string module)
        {
            if (!IsPythonInstalled())
                return false;

            string packagesDir = Path.Combine(Query.EmbeddedPythonHome(), "Lib", "site-packages");
            string moduleDir = Path.Combine(packagesDir, module);
            bool installed = Directory.Exists(moduleDir) && File.Exists(Path.Combine(moduleDir, "__init__.py"));
            installed |= File.Exists(Path.Combine(packagesDir, module.Replace("_", "-") + ".egg-link"));
            return installed;
        }

        /***************************************************/
    }
}
