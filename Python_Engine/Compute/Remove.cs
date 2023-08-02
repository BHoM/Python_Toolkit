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
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {

        [Description("Remove a named BHoM Python kernel.")]
        [Input("kernelName", "The name of the kernel to remove.")]
        public static void RemoveKernel(string kernelName)
        {
            string kernelPath = Path.Combine(Query.DirectoryKernels(), kernelName);
            if (Directory.Exists(kernelPath))
                Directory.Delete(kernelPath, true);
        }

        [Description("Remove all BHoM Python kernels.")]
        public static void RemoveAllKernels()
        {
            DirectoryInfo di = new DirectoryInfo(Query.DirectoryKernels());
            foreach (FileInfo file in di.EnumerateFiles())
            {
                file.Delete();
            }
            foreach (DirectoryInfo dir in di.EnumerateDirectories())
            {
                dir.Delete(true);
            }
        }

        [Description("Remove the named BHoM Python virtual environment.")]
        [Input("envName", "The name of the BHoM Python virtual environment to remove.")]
        public static void RemoveVirtualEnvironment(string envName)
        {
            string envPath = Path.Combine(Query.DirectoryEnvironments(), envName);
            if (Directory.Exists(envPath))
                Directory.Delete(envPath, true);
        }

        [Description("Completely remove the base BHoM Python environment.")]
        public static void RemoveBaseEnvironment()
        {
            string basePath = Path.Combine(Query.DirectoryEnvironments(), Query.ToolkitName());
            if (Directory.Exists(basePath))
                Directory.Delete(basePath, true);
        }

        [Description("Remove all BHoM Python environments.")]
        public static void RemoveAllEnvironments()
        {
            DirectoryInfo di = new DirectoryInfo(Query.DirectoryEnvironments());
            foreach (FileInfo file in di.EnumerateFiles())
            {
                file.Delete();
            }
            foreach (DirectoryInfo dir in di.EnumerateDirectories())
            {
                dir.Delete(true);
            }
        }

        [Description("Completely remove all BHoM-related Python environments and kernels.")]
        public static void RemoveEverything()
        {
            RemoveAllKernels();
            RemoveAllEnvironments();
        }
    }
}
