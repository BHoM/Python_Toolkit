/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2025, the respective contributors. All rights reserved.
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
using BH.oM.Base.Attributes;
using System.Collections.Generic;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get the URL for the embeddable package containing the given version of Python.")]
        [Input("version", "The version of Python to retrieve the URL.")]
        [Output("url", "The url for the matching Python version.")]
        public static string EmbeddableURL(this PythonVersion version)
        {
            // See the PythonVersion enum for why most of these are commented out.
            Dictionary<PythonVersion, string> versions = new Dictionary<PythonVersion, string>()
            {
                //{ PythonVersion.v3_7_2,   "https://www.python.org/ftp/python/3.7.2/python-3.7.2rc1-amd64.exe" },
                /*{ PythonVersion.v3_7_3,   "https://www.python.org/ftp/python/3.7.3/python-3.7.3rc1-amd64.exe" },
                { PythonVersion.v3_7_4,   "https://www.python.org/ftp/python/3.7.4/python-3.7.4rc2-amd64.exe" },
                { PythonVersion.v3_7_5,   "https://www.python.org/ftp/python/3.7.5/python-3.7.5rc1-amd64.exe" },
                { PythonVersion.v3_7_6,   "https://www.python.org/ftp/python/3.7.6/python-3.7.6rc1-amd64.exe" },
                { PythonVersion.v3_7_7,   "https://www.python.org/ftp/python/3.7.7/python-3.7.7rc1-amd64.exe" },
                { PythonVersion.v3_7_8,   "https://www.python.org/ftp/python/3.7.8/python-3.7.8rc1-amd64.exe" },*/
                { PythonVersion.v3_7,   "https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe" },
                /*{ PythonVersion.v3_8_0,   "https://www.python.org/ftp/python/3.8.0/python-3.8.0rc1-amd64.exe" },
                { PythonVersion.v3_8_1,   "https://www.python.org/ftp/python/3.8.1/python-3.8.1rc1-amd64.exe" },
                { PythonVersion.v3_8_2,   "https://www.python.org/ftp/python/3.8.2/python-3.8.2rc2-amd64.exe" },
                { PythonVersion.v3_8_3,   "https://www.python.org/ftp/python/3.8.3/python-3.8.3rc1-amd64.exe" },
                { PythonVersion.v3_8_4,   "https://www.python.org/ftp/python/3.8.4/python-3.8.4rc1-amd64.exe" },
                { PythonVersion.v3_8_5,   "https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe" },
                { PythonVersion.v3_8_6,   "https://www.python.org/ftp/python/3.8.6/python-3.8.6rc1-amd64.exe" },
                { PythonVersion.v3_8_7,   "https://www.python.org/ftp/python/3.8.7/python-3.8.7rc1-amd64.exe" },
                { PythonVersion.v3_8_8,   "https://www.python.org/ftp/python/3.8.8/python-3.8.8rc1-amd64.exe" },*/
                { PythonVersion.v3_8,   "https://www.python.org/ftp/python/3.8.9/python-3.8.9-amd64.exe" },
                /*{ PythonVersion.v3_9_0,   "https://www.python.org/ftp/python/3.9.0/python-3.9.0rc2-amd64.exe" },
                { PythonVersion.v3_9_1,   "https://www.python.org/ftp/python/3.9.1/python-3.9.1rc1-amd64.exe" },
                { PythonVersion.v3_9_2,   "https://www.python.org/ftp/python/3.9.2/python-3.9.2rc1-amd64.exe" },
                { PythonVersion.v3_9_3,   "https://www.python.org/ftp/python/3.9.3/python-3.9.3-amd64.exe" },
                { PythonVersion.v3_9_4,   "https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe" },
                { PythonVersion.v3_9_5,   "https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe" },
                { PythonVersion.v3_9_6,   "https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe" },
                { PythonVersion.v3_9_7,   "https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe" },
                { PythonVersion.v3_9_8,   "https://www.python.org/ftp/python/3.9.8/python-3.9.8-amd64.exe" },
                { PythonVersion.v3_9_9,   "https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe" },*/
                { PythonVersion.v3_9,  "https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe" },
                /*{ PythonVersion.v3_10_0,  "https://www.python.org/ftp/python/3.10.0/python-3.10.0rc2-amd64.exe" },
                { PythonVersion.v3_10_1,  "https://www.python.org/ftp/python/3.10.1/python-3.10.1-amd64.exe" },
                { PythonVersion.v3_10_2,  "https://www.python.org/ftp/python/3.10.2/python-3.10.2-amd64.exe" },
                { PythonVersion.v3_10_3,  "https://www.python.org/ftp/python/3.10.3/python-3.10.3-amd64.exe" },
                { PythonVersion.v3_10_4,  "https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe" },
                { PythonVersion.v3_10_5,  "https://www.python.org/ftp/python/3.10.5/python-3.10.5-amd64.exe" },
                { PythonVersion.v3_10_6,  "https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe" },
                { PythonVersion.v3_10_7,  "https://www.python.org/ftp/python/3.10.7/python-3.10.7-amd64.exe" },
                { PythonVersion.v3_10_8,  "https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe" },
                { PythonVersion.v3_10_9,  "https://www.python.org/ftp/python/3.10.9/python-3.10.9-amd64.exe" },
                { PythonVersion.v3_10_10, "https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe" },*/
                { PythonVersion.v3_10, "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" },
                /*{ PythonVersion.v3_11_0,  "https://www.python.org/ftp/python/3.11.0/python-3.11.0rc2-amd64.exe" },
                { PythonVersion.v3_11_1,  "https://www.python.org/ftp/python/3.11.1/python-3.11.1-amd64.exe" },
                { PythonVersion.v3_11_2,  "https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe" },
                { PythonVersion.v3_11_3,  "https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe" },*/
                { PythonVersion.v3_11,  "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe" },
            };

            return versions[version];
        }
    }
}



