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

using System.Collections.Generic;
using BH.oM.Reflection.Attributes;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get the URL for the embeddable package containing the given version of Python.")]
        [Input("version", "The version of Python to retrieve the URL. This should be in the format \"MAJOR.MINOR.PATCH\".")]
        [Output("url", "The url for the matching Python version.")]
        public static string EmbeddableURL(string version)
        {
            Dictionary<string, string> versions = new Dictionary<string, string>()
            {
                { "3.6.0", "https://www.python.org/ftp/python/3.6.0/python-3.6.0-embed-amd64.zip" },
                { "3.6.1", "https://www.python.org/ftp/python/3.6.1/python-3.6.1-embed-amd64.zip" },
                { "3.6.2", "https://www.python.org/ftp/python/3.6.2/python-3.6.2-embed-amd64.zip" },
                { "3.6.3", "https://www.python.org/ftp/python/3.6.3/python-3.6.3-embed-amd64.zip" },
                { "3.6.4", "https://www.python.org/ftp/python/3.6.4/python-3.6.4-embed-amd64.zip" },
                { "3.6.5", "https://www.python.org/ftp/python/3.6.5/python-3.6.5-embed-amd64.zip" },
                { "3.6.6", "https://www.python.org/ftp/python/3.6.6/python-3.6.6-embed-amd64.zip" },
                { "3.6.7", "https://www.python.org/ftp/python/3.6.7/python-3.6.7-embed-amd64.zip" },
                { "3.6.8", "https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-amd64.zip" },
                { "3.7.0", "https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-amd64.zip" },
                { "3.7.1", "https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-amd64.zip" },
                { "3.7.3", "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip" },
                { "3.7.4", "https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip" },
                { "3.7.5", "https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-amd64.zip" },
                { "3.7.6", "https://www.python.org/ftp/python/3.7.6/python-3.7.6-embed-amd64.zip" },
                { "3.7.7", "https://www.python.org/ftp/python/3.7.7/python-3.7.7-embed-amd64.zip" },
                { "3.7.8", "https://www.python.org/ftp/python/3.7.8/python-3.7.8-embed-amd64.zip" },
                { "3.7.9", "https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-amd64.zip" },
                { "3.8.0", "https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip" },
                { "3.8.1", "https://www.python.org/ftp/python/3.8.1/python-3.8.1-embed-amd64.zip" },
                { "3.8.2", "https://www.python.org/ftp/python/3.8.2/python-3.8.2-embed-amd64.zip" },
                { "3.8.3", "https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-amd64.zip" },
                { "3.8.4", "https://www.python.org/ftp/python/3.8.4/python-3.8.4-embed-amd64.zip" },
                { "3.8.5", "https://www.python.org/ftp/python/3.8.5/python-3.8.5-embed-amd64.zip" },
                { "3.8.6", "https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-amd64.zip" },
                { "3.8.7", "https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-amd64.zip" },
                { "3.8.8", "https://www.python.org/ftp/python/3.8.8/python-3.8.8-embed-amd64.zip" },
                { "3.8.9", "https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-amd64.zip" },
                { "3.8.10", "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip" },
                { "3.9.0", "https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-amd64.zip" },
                { "3.9.1", "https://www.python.org/ftp/python/3.9.1/python-3.9.1-embed-amd64.zip" },
                { "3.9.2", "https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-amd64.zip" },
                { "3.9.4", "https://www.python.org/ftp/python/3.9.4/python-3.9.4-embed-amd64.zip" },
                { "3.9.5", "https://www.python.org/ftp/python/3.9.5/python-3.9.5-embed-amd64.zip" },
                { "3.9.6", "https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-amd64.zip" },
                { "3.9.7", "https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip" },
                { "3.10.0", "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip" },
            };

            // check that passed version is found/known
            if (!versions.ContainsKey(version))
            {
                BH.Engine.Reflection.Compute.RecordError($"Python {version} not found as an installable version of Python.");
                return "";
            }

            return versions[version];
        }
    }
}

