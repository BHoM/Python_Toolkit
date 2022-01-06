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

        public static PyObject Invoke(PyObject module, string method, Dictionary<string, object> args)
        {
            PyTuple pyargs = Convert.ToPyTuple(new object[]
            {
                args.FirstOrDefault().Value
            });

            PyDict kwargs = args.ToPython();

            if (method.Contains("."))
            {
                string[] chain = method.Split('.');
                for (int i = 0; i < chain.Length - 1; i++)
                    module = module.GetAttr(chain[i]);
                method = chain[chain.Length - 1];
            }

            if (args.Count > 0)
                return module.InvokeMethod(method, pyargs, kwargs);
            else
                return module.InvokeMethod(method);
        }

        /***************************************************/

        public static PyObject Invoke(PyObject module, string method, IEnumerable<object> args, Dictionary<string, object> kwargs)
        {
            PyTuple pyargs = Convert.ToPyTuple(args);
            PyDict pykwargs = Convert.ToPython(kwargs);

            if (method.Contains("."))
            {
                string[] chain = method.Split('.');
                for (int i = 0; i < chain.Length - 1; i++)
                    module = module.GetAttr(chain[i]);
                method = chain[chain.Length - 1];
            }

            return module.InvokeMethod(method, pyargs, pykwargs);
        }

        /***************************************************/
    }
}


