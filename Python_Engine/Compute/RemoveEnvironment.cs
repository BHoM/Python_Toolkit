/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2021, the respective contributors. All rights reserved.
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

using BH.oM.Python;
using BH.oM.Reflection.Attributes;

using System.ComponentModel;
using System.IO;
using System.Linq;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Remove the given BHoM Python environment.")]
        [Input("pythonEnvironment", "The name of the BHoM Python environment.")]
        [Input("run", "Set to True to remove environment.")]
        [Output("success", "True if environment successfully removed.")]
        public static bool RemoveEnvironment(this PythonEnvironment pythonEnvironment, bool run = false)
        {
            if (run)
            {
                DirectoryInfo directory = new DirectoryInfo(pythonEnvironment.EnvironmentDirectory());

                try
                {
                    directory.EnumerateFiles().ToList().ForEach(f => f.Delete());
                    directory.EnumerateDirectories().ToList().ForEach(d => d.Delete(true));
                    directory.Delete();
                }
                catch (System.Exception e)
                {
                    BH.Engine.Reflection.Compute.RecordError($"Cannot fully remove the environment. You may have the directory, or a file within it open in another program. Original error code: {e}");
                    return false;
                }

                return true;
            }
            return false;
        }
    }
}
