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

//using BH.oM.Reflection.Attributes;
//using System;
//using System.ComponentModel;
//using System.IO;

//namespace BH.Engine.Python
//{
//    public static partial class Query
//    {
//        /***************************************************/
//        /**** Public Methods                            ****/
//        /***************************************************/

//        [Description("Get the directory of the virtual environment for the given environment name.")]
//        [Input("virtualenvName", "The name of the virtual environment.")]
//        [Output("path", "The full path for the named virtual environment.")]
//        public static string VirtualEnvironmentPath(this string virtualenvName)
//        {
//            string environmentPath = Path.Combine(Query.EmbeddedPythonHome(), "envs", virtualenvName);
//            if (!Directory.Exists(environmentPath))
//            {
//                BH.Engine.Reflection.Compute.RecordWarning("This environment does not currently exist.");
//            }

//            return environmentPath;
//        }

//        /***************************************************/
//    }
//}

