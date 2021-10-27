//
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
// 

using BH.oM.Python;
using BH.oM.Reflection.Attributes;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        /***************************************************/
        /**** Public Methods                            ****/
        /***************************************************/

        [Description("Query the given BHoM Python environment for existence of the given package.")]
        [Input("pythonEnvironment", "The BHoM Python environment.")]
        [Input("package", "The package to check the environment for.")]
        [Output("isInstalled", "True if package is installed.")]
        public static bool IsPackageInstalled(this PythonEnvironment pythonEnvironment, string package)
        {
            if (!package.Contains("=="))
            {
                BH.Engine.Reflection.Compute.RecordError($"BHoM Python environments should be specific with the version of each package being used. Your {package} package must include a version number.");
                return false;
            }

            List<string> installedPackages = pythonEnvironment.InstalledPackages();

            if (installedPackages.Contains(package))
            {
                return true;
            }
            else
            {
                BH.Engine.Reflection.Compute.RecordNote($"{package} not present in given environment.");
            }
            return false;
        }

        /***************************************************/
    }
}
