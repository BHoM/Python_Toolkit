/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2024, the respective contributors. All rights reserved.
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
using BH.oM.Python.Enums;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("The location where BHoM extensions reside.")]
        [Output("The location where BHoM extensions reside.")]
        public static string DirectoryExtensions()
        {
            return Path.Combine(System.IO.Directory.GetParent(BH.Engine.Base.Query.BHoMFolder()).FullName, "Extensions");
        }

        [Description("The location where any BHoM-related Python kernels reside.")]
        [Output("The location where any BHoM-related Python kernels reside.")]
        public static string DirectoryKernels()
        {
            
            string dir = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.CommonApplicationData), "jupyter", "kernels");
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            return dir;
        }

        [Description("The location where any BHoM-related Python code resides.")]
        [Output("The location where any BHoM-related Python code resides.")]
        public static string DirectoryCode()
        {
            string dir = Path.Combine(Query.DirectoryExtensions(), "PythonCode");
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            return dir;
        }

        [Description("The location where any BHoM-related Python environment (or virtualenv) resides.")]
        [Output("The location where any BHoM-related Python environment (or virtualenv) resides.")]
        public static string DirectoryEnvironments()
        {
            string dir = Path.Combine(Query.DirectoryExtensions(), "PythonEnvironments");
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            return dir;
        }

        [PreviousVersion("8.0", "BH.Engine.Python.Query.DirectoryBaseEnvironment()")]
        [Description("The location where the base Python environment exists.")]
        [Output("The location where the base Python environment exists.")]
        public static string DirectoryBaseEnvironment(PythonVersion version = PythonVersion.v3_10)
        {
            return Path.Combine(Query.DirectoryEnvironments(), Query.ToolkitName(), version.ToString());
        }
    }
}



