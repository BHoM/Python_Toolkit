/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2022, the respective contributors. All rights reserved.
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

using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Obtain the Python_Toolkit BHoM Python Environment.")]
        [Output("environment", "A BHoM Python Environment.")]
        public static oM.Python.Environment PythonToolkitEnvironment()
        {
            // create names and paths for refenence
            string toolkitName = ToolkitName();
            string environmentDir = Path.Combine(EnvironmentsDirectory(), toolkitName);
            string codeDir = Path.Combine(CodeDirectory(), toolkitName);
            string packagesDir = Path.Combine(environmentDir, "Lib", "site-packages");
            string exe = Path.Combine(EnvironmentsDirectory(), toolkitName, "python.exe");
            string requirementsTxt = Path.Combine(codeDir, "requirements.txt");

            if (Query.Environment(toolkitName) == null)
            {
                BH.Engine.Base.Compute.RemoveEvent(BH.Engine.Base.Query.CurrentEvents().Last());

                // install env that doesn't currently exist
                oM.Python.Environment env = Compute.InstallEnvironment(
                    oM.Python.Enums.Version.v3_10_5,
                    toolkitName,
                    requirementsTxt
                );

                // copy code from PythonCode into Environment
                Compute.CopyDirectory(codeDir, Path.Combine(packagesDir, toolkitName), true);

                // install packages for this toolkit
                string installLog = env.InstallPackages(requirementsTxt);
                BH.Engine.Base.Compute.RecordNote(installLog);
            }

            return new oM.Python.Environment()
            {
                Name = toolkitName,
                Executable = exe,
            };
        }
    }
}
