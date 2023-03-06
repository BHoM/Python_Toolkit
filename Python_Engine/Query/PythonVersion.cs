/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2023; the respective contributors. All rights reserved.
 *
 * Each contributor holds copyright over their respective contributions.
 * The project versioning (Git) records all such contribution source information.
 *                                           
 *                                                                              
 * The BHoM is free software: you can redistribute it and/or modify         
 * it under the terms of the GNU Lesser General Public License as published by  
 * the Free Software Foundation; either version 3.0 of the License; or          
 * (at your option) any later version.                                          
 *                                                                              
 * The BHoM is distributed in the hope that it will be useful;              
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
 * GNU Lesser General Public License for more details.                          
 *                                                                            
 * You should have received a copy of the GNU Lesser General Public License     
 * along with this code. If not; see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
 */

using BH.oM.Python.Enums;
using BH.oM.Base.Attributes;

using System.Collections.Generic;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Get the enum form of a PythonVersion from it's string form. E.g. \"3.7.8\" would return BH.oM.Python.Enums.PythonVersion.v3_7_8\".")]
        [Input("versionString", "The string form of the Python version to retrieve.")]
        [Output("pythonVersion", "The corresponding version enum.")]
        public static PythonVersion PythonVersion(string versionString)
        {
            switch (versionString)
            {

                case "3.7.0":
                    return oM.Python.Enums.PythonVersion.v3_7_0;
                case "3.7.1":
                    return oM.Python.Enums.PythonVersion.v3_7_1;
                case "3.7.2":
                    return oM.Python.Enums.PythonVersion.v3_7_2;
                case "3.7.3":
                    return oM.Python.Enums.PythonVersion.v3_7_3;
                case "3.7.4":
                    return oM.Python.Enums.PythonVersion.v3_7_4;
                case "3.7.5":
                    return oM.Python.Enums.PythonVersion.v3_7_5;
                case "3.7.6":
                    return oM.Python.Enums.PythonVersion.v3_7_6;
                case "3.7.7":
                    return oM.Python.Enums.PythonVersion.v3_7_7;
                case "3.7.8":
                    return oM.Python.Enums.PythonVersion.v3_7_8;
                case "3.7.9":
                    return oM.Python.Enums.PythonVersion.v3_7_9;
                case "3.8.0":
                    return oM.Python.Enums.PythonVersion.v3_8_0;
                case "3.8.1":
                    return oM.Python.Enums.PythonVersion.v3_8_1;
                case "3.8.2":
                    return oM.Python.Enums.PythonVersion.v3_8_2;
                case "3.8.3":
                    return oM.Python.Enums.PythonVersion.v3_8_3;
                case "3.8.4":
                    return oM.Python.Enums.PythonVersion.v3_8_4;
                case "3.8.5":
                    return oM.Python.Enums.PythonVersion.v3_8_5;
                case "3.8.6":
                    return oM.Python.Enums.PythonVersion.v3_8_6;
                case "3.8.7":
                    return oM.Python.Enums.PythonVersion.v3_8_7;
                case "3.8.8":
                    return oM.Python.Enums.PythonVersion.v3_8_8;
                case "3.8.9":
                    return oM.Python.Enums.PythonVersion.v3_8_9;
                case "3.8.10":
                    return oM.Python.Enums.PythonVersion.v3_8_10;
                case "3.9.0":
                    return oM.Python.Enums.PythonVersion.v3_9_0;
                case "3.9.1":
                    return oM.Python.Enums.PythonVersion.v3_9_1;
                case "3.9.2":
                    return oM.Python.Enums.PythonVersion.v3_9_2;
                case "3.9.4":
                    return oM.Python.Enums.PythonVersion.v3_9_4;
                case "3.9.5":
                    return oM.Python.Enums.PythonVersion.v3_9_5;
                case "3.9.6":
                    return oM.Python.Enums.PythonVersion.v3_9_6;
                case "3.9.7":
                    return oM.Python.Enums.PythonVersion.v3_9_7;
                case "3.9.8":
                    return oM.Python.Enums.PythonVersion.v3_9_8;
                case "3.9.9":
                    return oM.Python.Enums.PythonVersion.v3_9_9;
                case "3.9.10":
                    return oM.Python.Enums.PythonVersion.v3_9_10;
                case "3.10.0":
                    return oM.Python.Enums.PythonVersion.v3_10_0;
                case "3.10.1":
                    return oM.Python.Enums.PythonVersion.v3_10_1;
                case "3.10.2":
                    return oM.Python.Enums.PythonVersion.v3_10_2;
                case "3.10.3":
                    return oM.Python.Enums.PythonVersion.v3_10_3;
                case "3.10.4":
                    return oM.Python.Enums.PythonVersion.v3_10_4;
                case "3.10.5":
                    return oM.Python.Enums.PythonVersion.v3_10_5;
                default:
                    return oM.Python.Enums.PythonVersion.Undefined;
            }
        }
    }
}

