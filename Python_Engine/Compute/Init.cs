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

using Python.Runtime;
using System.Collections.Generic;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static PyObject Init(dynamic type, Dictionary<string, object> parameters)
        {
            PyTuple pyargs = Convert.ToPyTuple(new object[]
            {
                parameters.FirstOrDefault().Value
            });

            PyDict kwargs = new PyDict();

            bool skip = true;
            foreach (var item in parameters)
            {
                if (skip)
                {
                    skip = false;
                    continue;
                }

                if (item.Value != null && !string.IsNullOrWhiteSpace(item.Value.ToString()))
                {
                    kwargs[item.Key] = Convert.IToPython(item.Value);
                }
            }

            if (parameters.Count > 0)
                return type.Invoke(pyargs, kwargs);
            else
                return type.Invoke(null, null);
        }

        /***************************************************/
    }
}

