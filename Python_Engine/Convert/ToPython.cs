/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2019, the respective contributors. All rights reserved.
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

namespace BH.Engine.Python
{
    public static partial class Convert
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static PyObject ToPython(object obj)
        {
            if (obj == null)
                return Runtime.GetPyNone();
            switch (obj)
            {
                default: throw new NotImplementedException($"Type is not yet supported: { obj.GetType().Name}. Add it to 'ToPythonConversions'");
            }
        }

        /***************************************************/

        public static PyInt ToPython(int integer)
        {
            return new PyInt(integer);
        }

        /***************************************************/

        public static PyLong ToPython(long integer64)
        {
            return new PyLong(integer64);
        }

        /***************************************************/

        public static PyFloat ToPython(float floatingPoint)
        {
            return new PyFloat(floatingPoint);
        }

        /***************************************************/

        public static PyFloat ToPython(double floatingPoint)
        {
            return new PyFloat(floatingPoint);
        }

        /***************************************************/

        public static PyString ToPython(string text)
        {
            return new PyString(text);
        }

        /***************************************************/

        public static PyObject ToPython(bool boolean)
        {
            if (boolean)
                return new PyObject(Runtime.PyTrue);
            else
                return new PyObject(Runtime.PyFalse);
        }

        /***************************************************/

        public static PyTuple ToPython(ValueTuple<int> input)
        {
            var array = new PyObject[1];
            array[0] = ToPython(input.Item1);

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPython(ValueTuple<int, int> input)
        {
            var array = new PyObject[2];
            array[0] = ToPython(input.Item1);
            array[1] = ToPython(input.Item2);

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPython(ValueTuple<int, int, int> input)
        {
            var array = new PyObject[3];
            array[0] = ToPython(input.Item1);
            array[1] = ToPython(input.Item2);
            array[2] = ToPython(input.Item3);

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyList ToPython(Array input)
        {
            var array = new PyObject[input.Length];
            for (int i = 0; i < input.Length; i++)
            {
                array[i] = ToPython(input.GetValue(i));
            }

            return new PyList(array);
        }

        /***************************************************/
    }
}
