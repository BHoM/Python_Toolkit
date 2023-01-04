/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2023, the respective contributors. All rights reserved.
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

using BH.oM.Base.Attributes;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Create a header for a logging document.")]
        [Input("text", "A string to place into the header.")]
        [Output("header", "A header string.")]
        public static string LoggingHeader(string text)
        {
            StringBuilder sb = new StringBuilder();
            int maxLength = new List<int>() { text.Length, 54 }.Max();
            int innerLength = maxLength - 4;
            string topBottom = String.Concat(Enumerable.Repeat("#", maxLength + 4));
            sb.AppendLine();
            sb.AppendLine(topBottom);
            sb.AppendLine($"# {String.Format($"{{0,-{maxLength}}}", text)} #");
            sb.AppendLine($"# {String.Format($"{{0,-{maxLength}}}", System.DateTime.Now.ToString("s"))} #");
            sb.AppendLine($"# {String.Format($"{{0,-{maxLength}}}", $"BHoM version {BH.Engine.Base.Query.BHoMVersion()}")} #");
            sb.AppendLine(topBottom);
            return sb.ToString();
        }
    }
}

