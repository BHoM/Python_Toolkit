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

using FluentAssertions;
using BH.oM.Python;
using BH.oM.Base.Debugging;
using System.Diagnostics;
using System.IO.Compression;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python.Compute
{
    public abstract class Base
    {
        protected string m_Root = null!;
        protected PythonEnvironment m_Environment = null!;
        private readonly Dictionary<string, string?> m_OriginalVariables = new();

        [OneTimeSetUp]
        public void EnsureManagedUV()
        {
            string? originalPath = Environment.GetEnvironmentVariable("PATH");
            try
            {
                BH.Engine.Base.Compute.ClearCurrentEvents();
                BH.Engine.Python.Compute.InstallUV(run: true);
                File.Exists(EngineQuery.UVExecutable()).Should().BeTrue();
                AssertNoErrors();
            }
            finally
            {
                Environment.SetEnvironmentVariable("PATH", originalPath);
                BH.Engine.Base.Compute.ClearCurrentEvents();
            }
        }

        [SetUp]
        public void SetUp()
        {
            string name = "bhom_install_remove_" + Guid.NewGuid().ToString("N");
            m_Root = Path.Combine(EngineQuery.DirectoryEnvironments(), name);
            Directory.CreateDirectory(m_Root);
            m_Environment = new PythonEnvironment
            {
                Name = name,
                Executable = Path.Combine(m_Root, ".venv", "Scripts", "python.exe")
            };
            Run(EngineQuery.UVExecutable(), "venv", "--no-project", "--no-python-downloads", Path.Combine(m_Root, ".venv"));
            SetVariable("JUPYTER_DATA_DIR", Path.Combine(m_Root, "jupyter"));
            SetVariable("JUPYTER_PATH", Path.Combine(m_Root, "jupyter"));
            SetVariable("UV_TOOL_DIR", Path.Combine(m_Root, "tools"));
            SetVariable("UV_TOOL_BIN_DIR", Path.Combine(m_Root, "bin"));
            SetVariable("UV_CACHE_DIR", Path.Combine(m_Root, "cache"));
            string conflictingUV = Path.Combine(m_Root, "conflicting-uv");
            Directory.CreateDirectory(conflictingUV);
            File.WriteAllText(Path.Combine(conflictingUV, "uv.cmd"), "@echo UV from PATH must not be used 1>&2\r\n@exit /b 99\r\n");
            SetVariable("PATH", conflictingUV + Path.PathSeparator + Environment.GetEnvironmentVariable("PATH"));
            BH.Engine.Base.Compute.ClearCurrentEvents();
        }

        [TearDown]
        public void TearDown()
        {
            foreach (var variable in m_OriginalVariables)
                Environment.SetEnvironmentVariable(variable.Key, variable.Value);
            m_OriginalVariables.Clear();
            if (Directory.Exists(m_Root))
                Directory.Delete(m_Root, true);
            BH.Engine.Base.Compute.ClearCurrentEvents();
        }

        protected void PrepareToolPackages()
        {
            foreach (string tool in new[] { "ruff", "jupyterlab", "sphinx" })
                CreateWheel(tool, "1.0.0");
            SetVariable("UV_FIND_LINKS", Path.Combine(m_Root, "wheels"));
            SetVariable("UV_OFFLINE", "true");
        }

        protected void PreparePackageVersions()
        {
            CreateWheel("bhom_repeat_package", "1.0.0");
            CreateWheel("bhom_repeat_package", "2.0.0");
            SetVariable("UV_FIND_LINKS", Path.Combine(m_Root, "wheels"));
            SetVariable("UV_OFFLINE", "true");
        }

        private void CreateWheel(string name, string version)
        {
            string wheels = Path.Combine(m_Root, "wheels");
            Directory.CreateDirectory(wheels);
            using var archive = ZipFile.Open(Path.Combine(wheels, $"{name}-{version}-py3-none-any.whl"), ZipArchiveMode.Create);
            string info = $"{name}-{version}.dist-info";
            var files = new Dictionary<string, string>
            {
                [$"{name}.py"] = "def main():\n    pass\n",
                [$"{info}/METADATA"] = $"Metadata-Version: 2.1\nName: {name.Replace('_', '-')}\nVersion: {version}\n",
                [$"{info}/WHEEL"] = "Wheel-Version: 1.0\nGenerator: BHoM-tests\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
                [$"{info}/entry_points.txt"] = $"[console_scripts]\n{name} = {name}:main\n"
            };
            files[$"{info}/RECORD"] = string.Join("\n", files.Keys.Select(path => path + ",,")) + $"\n{info}/RECORD,,\n";
            foreach (var file in files)
            {
                using var writer = new StreamWriter(archive.CreateEntry(file.Key).Open());
                writer.Write(file.Value);
            }
        }

        protected string CreateLocalPackage(string folder)
        {
            string source = Path.Combine(m_Root, folder);
            Directory.CreateDirectory(source);
            File.WriteAllText(Path.Combine(source, "pyproject.toml"),
                "[build-system]\nrequires = [\"setuptools\"]\nbuild-backend = \"setuptools.build_meta\"\n"
                + "[project]\nname = \"bhom-local-package\"\nversion = \"1.0.0\"\n");
            File.WriteAllText(Path.Combine(source, "bhom_local_package.py"), "VALUE = 1\n");
            return source;
        }

        protected void CreateProject()
        {
            File.WriteAllText(Path.Combine(m_Root, "pyproject.toml"),
                "[project]\nname = \"bhom-test-project\"\nversion = \"1.0.0\"\nrequires-python = \">=3.10\"\ndependencies = []\n");
        }

        protected string PackageMetadata(string name, string version)
        {
            return Path.Combine(m_Root, ".venv", "Lib", "site-packages", $"{name}-{version}.dist-info", "METADATA");
        }

        protected void SetVariable(string name, string value)
        {
            if (!m_OriginalVariables.ContainsKey(name))
                m_OriginalVariables.Add(name, Environment.GetEnvironmentVariable(name));
            Environment.SetEnvironmentVariable(name, value);
        }

        protected static void WithIsolatedDirectory(string directory, Action test)
        {
            string backup = directory + ".test-backup-" + Guid.NewGuid().ToString("N");
            bool existed = Directory.Exists(directory);
            if (existed)
                Directory.Move(directory, backup);
            try
            {
                Directory.CreateDirectory(directory);
                test();
            }
            finally
            {
                try
                {
                    if (Directory.Exists(directory))
                        Directory.Delete(directory, true);
                }
                finally
                {
                    if (existed)
                        Directory.Move(backup, directory);
                }
            }
        }

        protected static void AssertNoErrors()
        {
            BH.Engine.Base.Query.CurrentEvents().Where(e => e.Type == EventType.Error).Select(e => e.Message).Should().BeEmpty();
        }

        protected static void AssertWarningWithoutErrors()
        {
            AssertNoErrors();
            BH.Engine.Base.Query.CurrentEvents().Should().Contain(e => e.Type == EventType.Warning);
        }

        protected static string Run(string executable, params string[] arguments)
        {
            using var process = new Process
            {
                StartInfo = new ProcessStartInfo(executable)
                {
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                }
            };
            foreach (string argument in arguments)
                process.StartInfo.ArgumentList.Add(argument);
            process.Start();
            Task<string> stdout = process.StandardOutput.ReadToEndAsync();
            Task<string> stderr = process.StandardError.ReadToEndAsync();
            if (!process.WaitForExit(120000))
            {
                process.Kill(entireProcessTree: true);
                Assert.Fail($"Test command timed out: {executable} {string.Join(" ", arguments)}");
            }
            Task.WaitAll(stdout, stderr);
            process.ExitCode.Should().Be(0, stderr.Result);
            return stdout.Result.Trim();
        }
    }
}
