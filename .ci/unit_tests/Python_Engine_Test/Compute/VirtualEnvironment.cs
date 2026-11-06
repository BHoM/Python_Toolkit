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

using BH.oM.Base.Debugging;
using BH.oM.Python;
using FluentAssertions;
using EngineCompute = BH.Engine.Python.Compute;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python.Compute
{
    [NonParallelizable]
    public class VirtualEnvironment
    {
        private readonly Dictionary<string, string?> m_OriginalVariables = [];
        private string m_TestDirectory = null!;
        private string m_Name = null!;
        private string m_Directory = null!;

        [OneTimeSetUp]
        public void SetUpTools()
        {
            m_TestDirectory = Path.Combine(Path.GetTempPath(), "bhom_lifecycle_" + Guid.NewGuid().ToString("N"));
            foreach (string variable in new[] { "UV_TOOL_DIR", "UV_TOOL_BIN_DIR", "JUPYTER_DATA_DIR", "JUPYTER_PATH" })
            {
                m_OriginalVariables[variable] = Environment.GetEnvironmentVariable(variable);
                Environment.SetEnvironmentVariable(variable, Path.Combine(m_TestDirectory, variable));
            }
        }

        [SetUp]
        public void SetUp()
        {
            m_Name = "bhom_lifecycle_" + Guid.NewGuid().ToString("N");
            m_Directory = Path.Combine(EngineQuery.DirectoryEnvironments(), m_Name);
            BH.Engine.Base.Compute.ClearCurrentEvents();
        }

        [TearDown]
        public void CleanUpEnvironment()
        {
            if (EngineQuery.VirtualEnvironmentExists(m_Name))
                EngineCompute.RemoveVirtualEnvironment(m_Name, run: true);
            if (Directory.Exists(m_Directory))
                Directory.Delete(m_Directory, true);
            BH.Engine.Base.Compute.ClearCurrentEvents();
        }

        [OneTimeTearDown]
        public void CleanUpTools()
        {
            foreach (var variable in m_OriginalVariables)
                Environment.SetEnvironmentVariable(variable.Key, variable.Value);
            if (Directory.Exists(m_TestDirectory))
                Directory.Delete(m_TestDirectory, true);
            if (Directory.Exists(EngineQuery.DirectoryTools()))
                Directory.Delete(EngineQuery.DirectoryTools(), true);
        }

        [Test]
        public void VirtualEnvironment_FromTargetVersion_CreatesReloadsAndRemovesEnvironmentAndKernel()
        {
            PythonEnvironment venv = EngineCompute.VirtualEnvironment("3.11", m_Name);
            venv.Should().NotBeNull();
            File.Exists(venv.Executable).Should().BeTrue();
            EngineQuery.Version(venv).Should().StartWith("3.11.");
            EngineCompute.RunPythonString(venv, "import ipykernel; print('ready')").Should().Be("ready");
            EngineCompute.VirtualEnvironment("3.11", m_Name, reload: true).Executable.Should().Be(venv.Executable);
            File.Exists(KernelFile()).Should().BeTrue();

            EngineCompute.RemoveVirtualEnvironment(m_Name, run: true);

            Directory.Exists(Path.Combine(m_Directory, ".venv")).Should().BeFalse();
            File.Exists(KernelFile()).Should().BeFalse();
            AssertNoErrors();
        }

        [Test]
        public void VirtualEnvironment_FromTOML_CreatesReloadsAndRemovesEnvironmentAndKernel()
        {
            string packageDirectory = Path.Combine(m_Directory, "src", m_Name);
            Directory.CreateDirectory(packageDirectory);
            File.WriteAllText(Path.Combine(packageDirectory, "__init__.py"), "");
            File.WriteAllText(Path.Combine(m_Directory, "README.md"), "");
            string tomlFile = Path.Combine(m_Directory, "pyproject.toml");
            File.WriteAllText(tomlFile,
                $"[project]\nname = '{m_Name}'\nversion = '0.1.0' # project version\nreadme = 'README.md'\n"
                + "requires-python = '>=3.11,<3.12'\ndependencies = []\n"
                + "[build-system]\nrequires = ['hatchling']\nbuild-backend = 'hatchling.build'\n"
                + "[tool.bhom]\nversion = 'leave-this-alone'\n");

            PythonEnvironment venv = EngineCompute.VirtualEnvironment(tomlFile, reload: false);
            venv.Should().NotBeNull();
            string version = BH.Engine.Base.Query.BHoMVersion();
            File.ReadAllText(tomlFile).Should().Contain($"version = \"{version}\" # project version")
                .And.Contain("version = 'leave-this-alone'");
            EngineCompute.RunPythonString(venv,
                $"import importlib.metadata; print(importlib.metadata.version('{m_Name}'))").Should().Be(version);

            EngineCompute.VirtualEnvironment(tomlFile, reload: false).Should().NotBeNull();
            File.Exists(Path.Combine(packageDirectory, "__init__.py")).Should().BeTrue();
            EngineCompute.VirtualEnvironment(tomlFile, reload: true).Executable.Should().Be(venv.Executable);
            EngineCompute.RemoveVirtualEnvironment(m_Name, run: true);

            Directory.Exists(Path.Combine(m_Directory, ".venv")).Should().BeFalse();
            File.Exists(KernelFile()).Should().BeFalse();
            AssertNoErrors();
        }

        private string KernelFile()
        {
            return Path.Combine(Environment.GetEnvironmentVariable("JUPYTER_DATA_DIR")!, "kernels", m_Name, "kernel.json");
        }

        private static void AssertNoErrors()
        {
            BH.Engine.Base.Query.CurrentEvents().Where(e => e.Type == EventType.Error).Select(e => e.Message).Should().BeEmpty();
        }
    }
}
