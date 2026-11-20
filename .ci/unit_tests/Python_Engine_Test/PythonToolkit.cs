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
using BH.Tests.Engine.Python.Compute;
using FluentAssertions;
using System.Text.RegularExpressions;
using EngineCompute = BH.Engine.Python.Compute;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python
{
    [NonParallelizable]
    public class PythonToolkit : Base
    {
        [Test, Order(9998)]
        [Ignore("Disabled for now.")]
        public void ZZZ_InstallPythonToolkitVenv()
        {
            BH.Engine.Base.Compute.ClearCurrentEvents();
            EngineCompute.InstallPythonToolkitVenv(run: true, reload: false);
            AssertNoErrors();
        }

        [Test, Order(9999)]
        [Ignore("Disabled for now.")]
        public void ZZZ_Pytest()
        {
            BH.Engine.Base.Compute.ClearCurrentEvents();
            EngineCompute.InstallPythonToolkitVenv(run: true, reload: false);
            DirectoryInfo? repository = new(TestContext.CurrentContext.TestDirectory);
            while (repository != null && !File.Exists(Path.Combine(repository.FullName, "Python_Engine", "Python", "pyproject.toml")))
                repository = repository.Parent;
            repository.Should().NotBeNull("the toolkit sources must be available to run pytest");

            string source = Path.Combine(repository!.FullName, "Python_Engine", "Python");
            string name = "bhom_pytest_" + Guid.NewGuid().ToString("N");
            string directory = Path.Combine(EngineQuery.DirectoryEnvironments(), name);
            BH.Engine.Base.Compute.ClearCurrentEvents();

            try
            {
                PythonEnvironment venv = EngineCompute.InstallPythonToolkitVenv(run: true, reload: false);

                venv.Should().NotBeNull("environment installation must succeed: {0}",
                    string.Join(Environment.NewLine, BH.Engine.Base.Query.CurrentEvents().Where(e => e.Type == EventType.Error).Select(e => e.Message)));

                var result = EngineCompute.RunCommandStdout(
                    $"set \"SKIP_LONG_PYTEST=1\" && \"{venv.Executable}\" -m pytest -ra",
                    startDirectory: directory, timeoutMinutes: 10);
                string output = result.Item1 + Environment.NewLine + result.Item2;
                TestContext.Progress.WriteLine(output);

                Match warnings = Regex.Match(output,
                    @"(?ms)^=+[ \t]*warnings summary[ \t]*=+\r?\n(?<warnings>.*?)(?=^=+|\z)");
                if (warnings.Success)
                    BH.Engine.Base.Compute.RecordWarning(warnings.Groups["warnings"].Value.Trim());
                if (result.Item3 != 0)
                    BH.Engine.Base.Compute.RecordError($"Pytest failed (exit code {result.Item3}).\n{output}");

                result.Item3.Should().Be(0, "pytest must pass:\n{0}", output);
                BH.Engine.Base.Query.CurrentEvents().Where(e => e.Type == EventType.Error)
                    .Select(e => e.Message).Should().BeEmpty();
            }
            finally
            {
                if (EngineQuery.VirtualEnvironmentExists(name))
                    EngineCompute.RemoveVirtualEnvironment(name, run: true);
                if (Directory.Exists(directory))
                    Directory.Delete(directory, true);
            }
        }
    }
}
