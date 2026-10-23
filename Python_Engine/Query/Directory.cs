/*
 * This file is part of the Buildings and Habitats object Model (BHoM)
 * Copyright (c) 2015 - 2026, the respective contributors. All rights reserved.
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
using BH.oM.Python.Enums;
using System.ComponentModel;
using System.IO;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("The location where BHoM extensions reside.")]
        [Output("path", "The location where BHoM extensions reside.")]
        public static string DirectoryExtensions()
        {
            return Path.Combine(System.IO.Directory.GetParent(BH.Engine.Base.Query.BHoMFolder()).FullName, "Extensions");
        }

        [Description("The location where any BHoM-related Python environment (or virtualenv) resides.")]
        [Output("path", "The location where any BHoM-related Python environment (or virtualenv) resides.")]
        public static string DirectoryEnvironments()
        {
            string dir = Path.Combine(Query.DirectoryExtensions(), "Python");
            if (!Directory.Exists(dir))
                Directory.CreateDirectory(dir);
            return dir;
        }
    }
}
