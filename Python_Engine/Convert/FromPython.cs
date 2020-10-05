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
                return null;

            IntPtr handle = obj.Handle;

            if (PyInt.IsIntType(obj))
                return FromPython(new PyInt(obj));
            else if (PyLong.IsLongType(obj))
                return FromPython(new PyLong(obj));
            else if (PyFloat.IsFloatType(obj))
                return FromPython(new PyFloat(obj));
            else if (PyString.IsStringType(obj))
                return FromPython(new PyString(obj));
            else if (PyList.IsListType(obj))
                return FromPython(new PyList(obj));
            else if (PyDict.IsDictType(obj))
                return FromPython(new PyDict(obj));
            else if (PyTuple.IsTupleType(obj))
                return FromPython(new PyTuple(obj));
            else if (obj.IsIterable())
                return FromPython(new PyIter(obj));
            else if (Runtime.PyBool_Check(handle))
                return obj.As<bool>();
            else if (Runtime.PyNumber_Check(handle))
                return FromPython(new PyFloat(Runtime.PyNumber_Float(handle)));

            throw new Exception($"WHAT THE FUCK IS THIS {obj}");
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
                dynamic value = IFromPython(pyDict[pykey]);
                dict.Add(key, value);
            }
            return dict;
        }

        /***************************************************/

        public static List<object> FromPython(this PyTuple input)
        {
            List<object> cObject = new List<object>();
            foreach (PyObject item in input)
                cObject.Add(IFromPython(item));
            return cObject;
        }

        /***************************************************/

        public static List<object> FromPython(this PyList input)
        {
            List<object> cObject = new List<object>();
            foreach (PyObject item in input)
                cObject.Add(IFromPython(item));
            return cObject;
        }

        /***************************************************/

        public static List<object> FromPython(this PyIter input)
        {
            List<object> cObject = new List<object>();
            foreach(PyObject item in input)
                cObject.Add(IFromPython(item));
            return cObject;
        }

        /***************************************************/

    }
}
