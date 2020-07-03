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
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static void PipInstall(string module_name, string version = "", bool force = false, string findLinks = "")
        {
            if (Query.IsModuleInstalled(module_name) && !force)
                return;

            string pipPath = Path.Combine(Query.EmbeddedPythonHome(), "Scripts", "pip3");
            string forceInstall = force ? "--force-reinstall" : "";
            if (version.Length > 0)
                version = $"=={version}";

            if (findLinks != "")
                findLinks = "-f " + findLinks;

            RunCommand($"{pipPath} install {module_name}{version} {findLinks} {forceInstall}");
        }

        /***************************************************/
    }
}
