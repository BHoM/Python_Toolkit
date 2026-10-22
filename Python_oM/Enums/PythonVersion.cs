/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
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
    public enum PythonVersion
    {
        [Description("Undefined")]
        Undefined,
        [Description("3.7")]
        v3_7,
        [Description("3.8")]
        v3_8,
        [Description("3.9")]
        v3_9,
        [Description("3.10")]
        v3_10,
        [Description("3.11")]
        v3_11,
        [Description("3.12")]
        v3_12,
        [Description("3.13")]
        v3_13,
        [Description("3.14")]
        v3_14,
    }
}
