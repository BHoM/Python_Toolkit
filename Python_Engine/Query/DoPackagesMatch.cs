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

using System.Collections.Generic;
using System.ComponentModel;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("Determine whether one list of PythonPackages matches another list of PythonPackages.")]
        [Input("packages1", "The first list of PythonPackages.")]
        [Input("packages2", "The second list of PythonPackages.")]
        [Output("matching", "True if the lists match.")]
        public static bool DoPackagesMatch(this List<PythonPackage> packages1, List<PythonPackage> packages2)
        {
            bool contains = true;
            
            foreach (PythonPackage pkg1 in packages1)
            {
                if (!packages2.PackageInList(pkg1))
                {
                    contains = false;
                }
            }

            foreach (PythonPackage pkg2 in packages2)
            {
                if (!packages1.PackageInList(pkg2))
                {
                    contains = false;
                }
            }

            return contains;
        }
    }
}
