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
//using System.Collections.Generic;
//using System.ComponentModel;
//using System.IO;

//namespace BH.Engine.Python
//{
//    public static partial class Compute
//    {
//        /***************************************************/
//        /**** Public Methods                            ****/
//        /***************************************************/

//        [Description("Run a Python script using a given environment, with the arguments given.")]
//        [Input("pythonExecutable", "The Python executable with which to run the Python script.")]
//        [Input("pythonScript", "The full path to the Python script.")]
//        [Input("args", "A list of arguments to be passed to the Python script.")]
//        [Output("result", "The stdout data from the executed Python script.")]
//        public static string RunPythonScript(string pythonExecutable, string pythonScript, List<string> args = null)
//        {
//            // Check that script exists at given path
//            if (!File.Exists(pythonScript))
//            {
//                Reflection.Compute.RecordError($"Python script does not exist at {pythonScript}.");
//            }

//            // construct command to be run
//            string cmd = $"{pythonExecutable} {pythonScript} {string.Join(" ", args)}";

//            // run the command
//            return RunCommandStdout(cmd);
//        }

//        /***************************************************/
//    }
//}

