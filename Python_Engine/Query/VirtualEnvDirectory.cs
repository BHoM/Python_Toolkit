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
using System.Xml.Linq;

namespace BH.Engine.Python
{
    public static partial class Query
    {
        [Description("The location where any BHoM generated Python environments reside.")]
        [Input("envName","The virtual environment name.")]
        [Output("The location where any BHoM generated Python environments reside.")]
        public static string VirtualEnvDirectory(string envName)
        {
            string directory = Path.Combine(Query.EnvironmentsDirectory(), envName);
            
            if (Directory.Exists(directory))
            {
                return directory;
            }
            
            BH.Engine.Base.Compute.RecordError($"The virtual environment directory for \"{envName}\" does not exist at \"{directory}\".");
            return null;
        }
    }
}


