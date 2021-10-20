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

//using System.Collections.Generic;
//using System.ComponentModel;
//using System.IO;
//using System.IO.Compression;
//using System.Linq;
//using BH.oM.Reflection.Attributes;

//namespace BH.Engine.Python
//{
//    public static partial class Compute
//    {
//        /***************************************************/
//        /**** Public Methods                            ****/
//        /***************************************************/

//        [Description("Install the embeddable Python into the target directory.")]
//        [Input("version", "The version of Python to be installed.")]
//        [Input("name", "The name of the directory into which Python will be installed.")]
//        [Input("packages", "A list of packages to be installed into this Python environment.")]
//        public static string InstallPythonTG(string version, string name, List<string> packages = null)
//        {
//            // Asset that name shouldn't have spaces
//            if (name.Any(x => System.Char.IsWhiteSpace(x)))
//            {
//                BH.Engine.Reflection.Compute.RecordError($"{name} cannot contain whitespace characters.");
//                return null;
//            }

//            // Set the location where Python will be installed
//            string targetDirectory = Path.Combine(Query.EmbeddedPythonHome(), name);
//            if (Directory.Exists(targetDirectory))
//            {
//                BH.Engine.Reflection.Compute.RecordWarning($"{name} environment already exists.");
//            }
//            System.IO.Directory.CreateDirectory(targetDirectory);
            
//            // Download the target Python version and Pip install file
//            string pythonZip = DownloadFile(Query.EmbeddableURL(version));
//            string getPip = DownloadFile("https://bootstrap.pypa.io/get-pip.py");

//            // Extract python into target directory and move files around to support normal Python behavior (as we're using embeddable, it needs some tweaking)
//            ZipFile.ExtractToDirectory(pythonZip, targetDirectory);

//            // allow pip on embedded python installation by unflagging python as embedded
//            // see https://github.com/pypa/pip/issues/4207#issuecomment-281236055
//            string[] pthFiles = Directory.GetFiles(targetDirectory, "*.*", SearchOption.AllDirectories).Where(s => s.EndsWith("._pth")).ToArray();
//            foreach (string file in pthFiles)
//            {
//                try
//                {
//                    File.Delete(file);
//                }
//                catch (System.Exception ex)
//                {
//                    BH.Engine.Reflection.Compute.RecordError(ex.ToString());
//                }
//            }
            
//            // Move *.dll and *.pyd files in the base Python environment into a DLL folder in that environments root directory.
//            string dllDirectory = Path.Combine(targetDirectory, "DLLs");
//            System.IO.Directory.CreateDirectory(dllDirectory);

//            foreach (string fileType in new List<string>() { ".dll", ".pyd" })
//            {
//                string[] files = Directory.GetFiles(targetDirectory, "*.*", SearchOption.AllDirectories).Where(s => s.EndsWith(fileType)).ToArray();
//                foreach (string file in files)
//                {
//                    if (!Path.GetFileName(file).Contains("python") && !Path.GetFileName(file).Contains("vcruntime"))
//                    {
//                        try
//                        {
//                            File.Move(file, Path.Combine(dllDirectory, Path.GetFileName(file)));
//                        }
//                        catch (System.Exception ex)
//                        {
//                            BH.Engine.Reflection.Compute.RecordError(ex.ToString());
//                        }
//                    }
//                }
//            }

//            // Install pip into environment
//            string pythonExecutable = Path.Combine(targetDirectory, "python.exe");
//            if (!RunCommandBool($"{pythonExecutable} {getPip} && exit"))
//            {
//                BH.Engine.Reflection.Compute.RecordError("Pip could not be installed for some reason");
//            }

//            // Install packages using Pip
//            if (!packages?.Any() != true)
//            {
//                if (!RunCommandBool($"{pythonExecutable} -m pip install --no-warn-script-location {System.String.Join(" ", packages)} && exit"))
//                {
//                    BH.Engine.Reflection.Compute.RecordError("Pip could not be installed for some reason");
//                }
//            }
//            return pythonExecutable;
//        }

//        /***************************************************/
//    }
//}

