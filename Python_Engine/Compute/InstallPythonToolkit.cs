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

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.IO;
using BH.oM.Reflection.Attributes;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Installs the necessary pre-requisites to use the Python Toolkit fully. This will install Python 3.7 to your system, to the C:/ProgramData/BHoM folder. This will take several minutes to complete")]
        [Input("run", "When you are ready to install Python, set this to true. Until this is set to true, this component will not run")]
        [Input("force", "If you have previously installed a version of Python Toolkit, you may need to force the component to run a new install. This can happen if your system loses files. This is set to false by default, which means if we can detect a previous Python install on your system we will not install Python this time. Set this to true to ignore this check")]
        [Output("success", "True is Python Toolkit has been successfully installer, false otherwise")]
        public static bool InstallPythonToolkit(bool run = false, bool force = false)
        {
            if (!run)
                return false;

            // Install python
            Console.WriteLine("Installing python 3.7 embedded...");
            Compute.Install(force).Wait();

            // Check the installation was successful 
            if (!Query.IsInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Coule not install Python");
                return false;
            }

            // Install pip
            Console.WriteLine("Installing pip...");
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Could not install pip");
                return false;
            }

            // install project jupyter
            Console.WriteLine("Installing jupyter...");
            Compute.PipInstall("jupyter");
            Compute.PipInstall("jupyterlab");
            Compute.PipInstall("pythonnet");

            return true;
        }

    }
}
