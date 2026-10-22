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

using BH.oM.Python.Enums;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.IO;

namespace BH.Tests.Engine.Python.Compute
{
    public class GenerateTOMLTests
    {
        [Test]
        [Description("Check whether the TOML file is generated as expected.")]
        public void GeneratesTOMLWithRequestedVersionAndPackages()
        {
            string temporaryDirectory = Path.Combine(Path.GetTempPath(), $"BHoM_PythonToolkit_{Guid.NewGuid():N}");
            Directory.CreateDirectory(temporaryDirectory);

            try
            {
                List<string> packages = ["numpy", "pandas"];
                string projectName = "test-project";
                string tomlPath = Path.Combine(temporaryDirectory, "pyproject.toml");

                string generatedPath = BH.Engine.Python.Compute.GenerateTOML(
                    PythonVersion.v3_10,
                    projectName,
                    packages,
                    temporaryDirectory);

                Assert.That(generatedPath, Is.EqualTo(tomlPath));
                Assert.That(File.Exists(tomlPath), Is.True, "The TOML file should be created in the requested directory.");

                string toml = File.ReadAllText(tomlPath);
                Assert.That(toml, Does.Contain("[project]"));
                Assert.That(toml, Does.Contain($"name = \"{projectName}\""));
                Assert.That(toml, Does.Contain("version = \"0.1.0\""));
                Assert.That(toml, Does.Contain($"requires-python = \"{PythonVersion.v3_10}\""));
                Assert.That(toml, Does.Contain("\"numpy\""));
                Assert.That(toml, Does.Contain("\"pandas\""));
            }
            finally
            {
                if (Directory.Exists(temporaryDirectory))
                {
                    Directory.Delete(temporaryDirectory, recursive: true);
                }
            }
        }

    }
}

