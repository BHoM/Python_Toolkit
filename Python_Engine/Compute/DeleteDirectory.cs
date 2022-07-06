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
    public static partial class Compute
    {
        [Description("Delete a directory and its contents.")]
        [Input("dir", "The directory to be removed.")]
        private static void DeleteDirectory(string dir)
        {
            DirectoryInfo dirInfo = new DirectoryInfo(dir);

            try
            {
                dirInfo.EnumerateFiles().ToList().ForEach(f => f.Delete());
                dirInfo.EnumerateDirectories().ToList().ForEach(d => d.Delete(true));
                dirInfo.Delete();
            }
            catch (System.Exception e)
            {
                BH.Engine.Base.Compute.RecordError($"Cannot fully remove the environment. You may have the directory, or a file within it open in another program. Original error code: {e}");
            }
        }
    }
}
