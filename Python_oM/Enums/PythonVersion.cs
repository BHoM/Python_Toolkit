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

using System.ComponentModel;

namespace BH.oM.Python.Enums
{
    // There are multiple specific versions here that are commented out - When installing, only one specific version (e.g 3.10.x) per minor python version (e.g 3.x) can be installed, and changes between specific versions are usually bug fixes and not breaking. however the specific versions are kept commented for posterity.
    public enum PythonVersion
    {
        [Description("Undefined")]
        Undefined,
        /*[Description("3.7.0")]
        v3_7_0,
        [Description("3.7.1")]
        v3_7_1,
        [Description("3.7.2")]
        v3_7_2,
        [Description("3.7.3")]
        v3_7_3,
        [Description("3.7.4")]
        v3_7_4,
        [Description("3.7.5")]
        v3_7_5,
        [Description("3.7.6")]
        v3_7_6,
        [Description("3.7.7")]
        v3_7_7,
        [Description("3.7.8")]
        v3_7_8,*/
        [Description("3.7")] //3.7.9
        v3_7,
        /*[Description("3.8.0")]
        v3_8_0,
        [Description("3.8.1")]
        v3_8_1,
        [Description("3.8.2")]
        v3_8_2,
        [Description("3.8.3")]
        v3_8_3,
        [Description("3.8.4")]
        v3_8_4,
        [Description("3.8.5")]
        v3_8_5,
        [Description("3.8.6")]
        v3_8_6,
        [Description("3.8.7")]
        v3_8_7,
        [Description("3.8.8")]
        v3_8_8,*/
        [Description("3.8")] //3.8.9
        v3_8,
        //[Description("3.8.10")]
        //v3_8_10,
        /*[Description("3.9.0")]
        v3_9_0,
        [Description("3.9.1")]
        v3_9_1,
        [Description("3.9.2")]
        v3_9_2,
        [Description("3.9.3")]
        v3_9_3,
        [Description("3.9.4")]
        v3_9_4,
        [Description("3.9.5")]
        v3_9_5,
        [Description("3.9.6")]
        v3_9_6,
        [Description("3.9.7")]
        v3_9_7,
        [Description("3.9.8")]
        v3_9_8,
        [Description("3.9.9")]
        v3_9_9,*/
        [Description("3.9")] //3.9.10
        v3_9,
        /*[Description("3.10.0")]
        v3_10_0,
        [Description("3.10.1")]
        v3_10_1,
        [Description("3.10.2")]
        v3_10_2,
        [Description("3.10.3")]
        v3_10_3,
        [Description("3.10.4")]
        v3_10_4,
        [Description("3.10.5")]
        v3_10_5,
        [Description("3.10.6")]
        v3_10_6,
        [Description("3.10.7")]
        v3_10_7,
        [Description("3.10.8")]
        v3_10_8,
        [Description("3.10.9")]
        v3_10_9,
        [Description("3.10.10")]
        v3_10_10,*/
        [Description("3.10")] //3.10.11
        v3_10,
        /*[Description("3.11.0")]
        v3_11_0,
        [Description("3.11.1")]
        v3_11_1,
        [Description("3.11.2")]
        v3_11_2,
        [Description("3.11.3")]
        v3_11_3,*/
        [Description("3.11")] //3.11.4
        v3_11,
    }
}


