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
        public static string EmbeddableURL(this Version version)
        {
            Dictionary<Version, string> versions = new Dictionary<Version, string>()
            {
                { oM.Python.Enums.Version.v3_7_0, "https://www.python.org/ftp/python/3.7.0/python-3.7.0-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_1, "https://www.python.org/ftp/python/3.7.1/python-3.7.1-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_2, "https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_3, "https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_4, "https://www.python.org/ftp/python/3.7.4/python-3.7.4-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_5, "https://www.python.org/ftp/python/3.7.5/python-3.7.5-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_6, "https://www.python.org/ftp/python/3.7.6/python-3.7.6-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_7, "https://www.python.org/ftp/python/3.7.7/python-3.7.7-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_8, "https://www.python.org/ftp/python/3.7.8/python-3.7.8-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_7_9, "https://www.python.org/ftp/python/3.7.9/python-3.7.9-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_0, "https://www.python.org/ftp/python/3.8.0/python-3.8.0-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_1, "https://www.python.org/ftp/python/3.8.1/python-3.8.1-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_2, "https://www.python.org/ftp/python/3.8.2/python-3.8.2-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_3, "https://www.python.org/ftp/python/3.8.3/python-3.8.3-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_4, "https://www.python.org/ftp/python/3.8.4/python-3.8.4-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_5, "https://www.python.org/ftp/python/3.8.5/python-3.8.5-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_6, "https://www.python.org/ftp/python/3.8.6/python-3.8.6-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_7, "https://www.python.org/ftp/python/3.8.7/python-3.8.7-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_8, "https://www.python.org/ftp/python/3.8.8/python-3.8.8-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_9, "https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_8_10, "https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_0, "https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_1, "https://www.python.org/ftp/python/3.9.1/python-3.9.1-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_2, "https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_4, "https://www.python.org/ftp/python/3.9.4/python-3.9.4-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_5, "https://www.python.org/ftp/python/3.9.5/python-3.9.5-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_6, "https://www.python.org/ftp/python/3.9.6/python-3.9.6-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_7, "https://www.python.org/ftp/python/3.9.7/python-3.9.7-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_8, "https://www.python.org/ftp/python/3.9.8/python-3.9.8-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_9, "https://www.python.org/ftp/python/3.9.9/python-3.9.9-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_9_10, "https://www.python.org/ftp/python/3.9.10/python-3.9.10-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_0, "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_1, "https://www.python.org/ftp/python/3.10.1/python-3.10.1-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_2, "https://www.python.org/ftp/python/3.10.2/python-3.10.2-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_3, "https://www.python.org/ftp/python/3.10.3/python-3.10.3-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_4, "https://www.python.org/ftp/python/3.10.4/python-3.10.4-embed-amd64.zip" },
                { oM.Python.Enums.Version.v3_10_5, "https://www.python.org/ftp/python/3.10.5/python-3.10.5-embed-amd64.zip" },
            };

            return versions[version];
        }
    }
}
