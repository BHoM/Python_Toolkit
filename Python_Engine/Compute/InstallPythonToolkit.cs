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

using System;
using System.Collections.Generic;
using BH.oM.Reflection.Attributes;
using System.ComponentModel;
using BH.oM.Reflection;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Installs the necessary pre-requisites to use the Python Toolkit fully. This will install Python 3.7 to your system, to the C:/ProgramData/BHoM folder.\n" +
            "This can take several minutes to complete")]
        [Input("run", "When you are ready to install Python, set this to true. Until this is set to true, this component will not run")]
        [Input("force", "If you have previously installed a version of Python Toolkit, you may need to force the component to run a new install. This can happen if your system loses files. This is set to false by default, which means if we can detect a previous Python install on your system we will not install Python this time. Set this to true to ignore this check")]
        [MultiOutput(0, "success", "True is Python Toolkit has been successfully installer, false otherwise")]
        [MultiOutput(1, "installedPackages", "A list of the Python packages which have been installed as part of this operation")]
        public static Output<bool, List<string>> InstallPythonToolkit(bool run = false, bool force = false)
        {
            bool success = false;
            List<string> installedPackages = new List<string>();
            if (!run)
                return new Output<bool, List<string>> { Item1 = success, Item2 = installedPackages };

            // Install python
            Console.WriteLine("Installing python 3.7 embedded...");
            Compute.InstallPython(force);

            // Check the installation was successful 
            if (!Query.IsPythonInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Coule not install Python");
                return new Output<bool, List<string>> { Item1 = success, Item2 = installedPackages };
            }
            installedPackages.Add("Python 3.7");

            // Install pip
            Console.WriteLine("Installing pip...");
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Could not install pip");
                return new Output<bool, List<string>> { Item1 = success, Item2 = installedPackages };
            }

            List<string> modules = new List<string>() { "jupyter", "jupyterlab", "pythonnet", "matplotlib", "numpy", "pandas" };

            // installing basic modules
            foreach (string module in modules)
            {
                Console.WriteLine($"Installing {module}");
                Compute.PipInstall(module);
                if (Query.IsModuleInstalled(module))
                    installedPackages.Add(module);
            }

            // install Python_Toolkit
            string pyBHoMpath = Path.Combine(Query.EmbeddedPythonHome(), "src", "Python_Toolkit");
            Compute.PipInstall($"-e {pyBHoMpath}", force: force);
            string m = "Python_Toolkit";
            if (Query.IsModuleInstalled(m))
                installedPackages.Add(m);

            ///////////////////////////// TEMPORARY
            ///
            Compute.PipInstall($" git+https://github.com/python-windrose/windrose", force: force);

            //////////////////////////////////////

            success = true;
            return new Output<bool, List<string>> { Item1 = success, Item2 = installedPackages };
        }

    }
}
