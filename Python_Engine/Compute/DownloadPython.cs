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

using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using Python.Runtime;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static bool DownloadPython()
        {
            string home = Query.EmbeddedPythonHome();
            if (!Directory.Exists(home))
                Directory.CreateDirectory(home);

            string destination = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "BHoM", $"{EMBEDDED_PYTHON}.zip");

            RunCommand($"curl {EMBEDDED_PYTHON_URL} -o {destination}");
            return true;
        }

        /***************************************************/
        /**** Public Fields                             ****/
        /***************************************************/

        public const string EMBEDDED_PYTHON_URL = @"https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip";

        /***************************************************/
    }
}
