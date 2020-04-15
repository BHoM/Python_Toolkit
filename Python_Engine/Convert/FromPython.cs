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
using System;
using System.Collections.Generic;

namespace BH.Engine.Python
{
    public static partial class Convert
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static object IFromPython(this PyObject obj)
        {
            if (obj == null || obj.IsNone())
                return Runtime.GetPyNone();

            return FromPython(obj as dynamic);
        }

        /***************************************************/

        public static T FromPython<T>(this PyObject obj)
        {
            return obj.As<T>();
        }

        /***************************************************/

        public static int FromPython(this PyInt integer)
        {
            return integer.ToInt32();
        }

        /***************************************************/

        public static long FromPython(this PyLong integer64)
        {
            return integer64.ToInt64();
        }

        /***************************************************/

        public static double FromPython(this PyFloat floatingPoint)
        {
            return floatingPoint.As<double>();
        }

        /***************************************************/

        public static string FromPython(this PyString text)
        {
            return text.As<string>();
        }

        /***************************************************/

        public static Dictionary<object, dynamic> FromPython(this PyDict pyDict)
        {
            var dict = new Dictionary<object, dynamic>();
            foreach (PyObject pykey in pyDict.Keys())
            {
                object key = IFromPython(pykey);
                dynamic value = FromPython<dynamic>(pyDict[pykey]);
                dict.Add(key, value);
            }
            return dict;
        }

        /***************************************************/

        public static List<dynamic> FromPython(this PyTuple input)
        {
            List<dynamic> cObject = new List<dynamic>();
            for (int i = 0; i < input.Length(); i++)
                cObject[i] = IFromPython(input[i]);
            return cObject;
        }

        /***************************************************/

        public static List<dynamic> FromPython(this PyList input)
        {
            List<dynamic> cObject = new List<dynamic>();
            for (int i = 0; i < input.Length(); i++)
                cObject[i] = IFromPython(input[i]);
            return cObject;
        }

        /***************************************************/
    }
}
