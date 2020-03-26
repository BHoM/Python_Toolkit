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
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Convert
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        public static PyTuple IToPyTuple(object obj)
        {
            if (obj == null)
                return new PyTuple();

            return ToPyTuple(obj as dynamic);
        }

        /***************************************************/

        public static PyTuple ToPyTuple(Array input)
        {
            PyObject[] array = new PyObject[input.Length];
            for (int i = 0; i < input.Length; i++)
            {
                array[i] = IToPython(input.GetValue(i));
            }

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPyTuple<T>(List<T> input)
        {
            PyObject[] array = new PyObject[input.Count()];
            for (int i = 0; i < input.Count(); i++)
            {
                array[i] = IToPython(input.ElementAt(i));
            }

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPyTuple<T>(ValueTuple<T> input)
        {
            PyObject[] array = new PyObject[1];
            array[0] = IToPython(input.Item1);

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPyTuple<T>(ValueTuple<T, T> input)
        {
            PyObject[] array = new PyObject[2];
            array[0] = IToPython(input.Item1);
            array[1] = IToPython(input.Item2);

            return new PyTuple(array);
        }

        /***************************************************/

        public static PyTuple ToPyTuple<T>(ValueTuple<T, T, T> input)
        {
            PyObject[] array = new PyObject[3];
            array[0] = IToPython(input.Item1);
            array[1] = IToPython(input.Item2);
            array[2] = IToPython(input.Item3);

            return new PyTuple(array);
        }

        /***************************************************/
    }
}
