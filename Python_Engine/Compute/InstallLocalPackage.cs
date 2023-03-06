/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2023, the respective contributors. All rights reserved.
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

using BH.oM.Base.Attributes;
using BH.oM.Python;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Install a virtualenv of the given configuration.")]
        [Input("env", "The environment to install the local package into.")]
        [Input("localPackage", "A local package to be installed in the target environment.")]
        [Output("output", "The stdout from the package installation procedure.")]
        public static string InstallLocalPackage(this PythonEnvironment env, string localPackage)
        {
            // check that the environment is valid
            if (!Query.EnvironmentExists(env))
            {
                BH.Engine.Base.Compute.RecordError($"A local package cannot be installed as the target environment ({env.Name}) does not exist!");
            }

            // check that given local package contains essential files
            if (Directory.Exists(localPackage))
            {
                BH.Engine.Base.Compute.RecordError($"The given local package ({localPackage}) does not exist!");
            }
            if (!File.Exists(Path.Combine(localPackage, "setup.py")))
            {
                BH.Engine.Base.Compute.RecordError($"The given local package ({localPackage}) does not contain a setup.py file!");
            }

            string output = Compute.RunCommandStdout($"{Modify.AddQuotesIfRequired(env.Executable)} -m pip install --no-warn-script-location -e {Modify.AddQuotesIfRequired(localPackage)}", hideWindows: true);

            return output;
        }
    }
}

