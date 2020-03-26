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

using Python.Runtime;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static PyObject Invoke(PyObject instanceOrModule, string method, Dictionary<string, object> args)
        {
            PyTuple pyargs = Convert.ToPyTuple(new object[]
            {
                args.FirstOrDefault().Value
            });

            PyDict kwargs = new PyDict();

            bool skip = true;
            foreach (var item in args)
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

            if (args.Count > 0)
                return instanceOrModule.InvokeMethod(method, pyargs, kwargs);
            else
                return instanceOrModule.InvokeMethod(method);
        }

        /***************************************************/
    }
}
