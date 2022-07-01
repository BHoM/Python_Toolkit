///*
// * This file is part of the Buildings and Habitats object Model (BHoM)
// * Copyright (c) 2015 - 2022, the respective contributors. All rights reserved.
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

//using BH.oM.Python;
//using BH.oM.Base.Attributes;

//using System.Collections.Generic;
//using System.ComponentModel;
//using System.IO;
//using System;
//using System.Linq;
//using BH.oM.Python.Enums;

//namespace BH.Engine.Python
//{
//    public static partial class Compute
//    {
//        [Description("Install a BHoM Python Environment.")]
//        [Input("name", "The name of the Python Environment.")]
//        [Input("version", "The version of Python to use for this Python Environment.")]
//        [Input("requirementsFile", "The path to the \"requirements.txt\" to install in this Python Environment.")]
//        [Input("codeDirectory", "The path to the custom BHoM code for this Python Environment.")]
//        [Input("force", "If the Environment already exists, recreate it rather than re-using it.")]
//        [Input("run", "Set to True to run the Environment installer.")]
//        [Output("environment", "A BHoM Python Environment object.")]
//        public static BH.oM.Python.Environment InstallEnvironment(string name, PythonVersion version, string requirementsFile = null, string codeDirectory = null, bool force = false, bool run = false)
//        {
//            if (name.Any(x => Char.IsWhiteSpace(x)))
//            {
//                BH.Engine.Base.Compute.RecordError($"A BHoM Python Environment name cannot contain whitespace characters.");
//                return null;
//            }

//            if (!run)
//            {
//                BH.Engine.Base.Compute.RecordNote($"This component will install a Python environment for {name} if it doesn't exist, or return the existing environment if it already exists in {Query.EnvironmentsDirectory()}.");
//                return null;
//            }

//            string basePythonExe = $"{Query.EnvironmentsDirectory()}\\Python_Toolkit\\python.exe";
//            string basePythonDir = $"{Query.EnvironmentsDirectory()}\\Python_Toolkit";






//            return new oM.Python.Environment()
//            {
//                Name = environment.Name,

//            }
//        }
//    }
//}

