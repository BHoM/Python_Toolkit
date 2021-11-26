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

        public static bool InstallPython(bool force = false)
        {
            bool success = true;
            string pythonHome = Query.EmbeddedPythonHome();

            // setup directories
            if (!Directory.Exists(pythonHome))
                Directory.CreateDirectory(pythonHome);

            // exit if python is already installed and installation is not forced
            if (!force && Query.IsPythonInstalled())
                return success;

            // download the python-embedded compressed archive
            string pythonZip = Path.Combine(pythonHome, $"python.zip");
            if (!File.Exists(pythonZip))
                Compute.DownloadPython();

            // inflate the archive
            try
            {
                ZipFile.ExtractToDirectory(pythonZip, pythonHome);

                // allow pip on embedded python installation by unflagging python as embedded
                // see https://github.com/pypa/pip/issues/4207#issuecomment-281236055
                File.Delete(Path.Combine(pythonHome, PYTHON_VERSION + "._pth"));
            }
            catch
            {
                success = false;
            }
            finally
            {
                // Clean up
                if (File.Exists(pythonZip))
                    File.Delete(pythonZip);
            }

            return success;
        }


        /***************************************************/
        /**** Public Fields                             ****/
        /***************************************************/

        public const string EMBEDDED_PYTHON = "python-3.7.3-embed-amd64";

        public const string PYTHON_VERSION = "python37";

        /***************************************************/
    }
}

