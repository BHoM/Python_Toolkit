///*
// * This file is part of the Buildings and Habitats object Model (BHoM)
// * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
// *
// * Each contributor holds copyright over their respective contributions.
// * The project versioning (Git) records all such contribution source information.
// *                                           
// *                                                                              
// * The BHoM is free software: you can redistribute it and/or modify         
// * it under the terms of the GNU Lesser General Public License as published by  
// * the Free Software Foundation, either version 3.0 of the License, or          
// * (at your option) any later version.                                          
// *                                                                              
// * The BHoM is distributed in the hope that it will be useful,              
// * but WITHOUT ANY WARRANTY; without even the implied warranty of               
// * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 
// * GNU Lesser General Public License for more details.                          
// *                                                                            
// * You should have received a copy of the GNU Lesser General Public License     
// * along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.      
// */

//using Python.Runtime;
//using System;
//using System.Collections.Generic;
//using System.ComponentModel;
//using System.Linq;

//namespace BH.Engine.Python
//{
//    public static partial class Convert
//    {
//        /***************************************************/
//        /**** Public Methods                            ****/
//        /***************************************************/

//        [Description("Convert a .NET object into a Python object.")]
//        public static PyTuple IToPyTuple(this object obj)
//        {
//            if (obj == null)
//                return new PyTuple();

//            return ToPyTuple(obj as dynamic);
//        }

//        /***************************************************/

//        [Description("Convert a .NET object into a Python object.")]
//        public static PyTuple ToPyTuple<T>(this IEnumerable<T> input)
//        {
//            PyObject[] array = new PyObject[input.Count()];
//            for (int i = 0; i < input.Count(); i++)
//            {
//                array[i] = IToPython(input.ElementAt(i));
//            }

//            return new PyTuple(array);
//        }

//        /***************************************************/

//        [Description("Convert a .NET object into a Python object.")]
//        public static PyTuple ToPyTuple<T>(this T[] input)
//        {
//            PyObject[] array = new PyObject[input.Length];
//            for (int i = 0; i < input.Length; i++)
//            {
//                array[i] = IToPython(input.GetValue(i));
//            }

//            return new PyTuple(array);
//        }

//        /***************************************************/

//        [Description("Convert a .NET object into a Python object.")]
//        public static PyTuple ToPyTuple<T>(this List<T> input)
//        {
//            PyObject[] array = new PyObject[input.Count()];
//            for (int i = 0; i < input.Count(); i++)
//            {
//                array[i] = IToPython(input.ElementAt(i));
//            }

//            return new PyTuple(array);
//        }

//        /***************************************************/
//    }
//}

