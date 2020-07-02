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

using System.Collections.Generic;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /*************************************/
        /**** Public Methods              ****/
        /*************************************/

        public static string PlotDiurnal(List<double> annualValues, string savePath, string grouping = "Daily", List<int> months = null, string title = null, string unit = null, string color = "black", string toneColor = "black", bool transparency = false)
        {
            months = months ?? new List<int>() { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 };

            Dictionary<string, object> kwargs = new Dictionary<string, object>
            {
                { "annual_values", annualValues },
                { "save_path", savePath },
                { "grouping", grouping },
                { "months", months },
                { "title", title },
                { "unit", unit },
                { "color", color },
                { "tone_color", toneColor },
                { "transparency", transparency }
            };
            return BH.Engine.Climate.Compute.Invoke("Diurnal.diurnal", kwargs).ToString();
        }

        /*************************************/
    }
}
