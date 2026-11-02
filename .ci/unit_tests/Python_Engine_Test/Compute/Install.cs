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
using EngineCompute = BH.Engine.Python.Compute;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python.Compute
{
    [NonParallelizable]
    public class InstallTests : InstallRemoveTestBase
    {
        [Test]
        public void InstallPythonToolkitVenv_InstallsAndReloadsToolkitEnvironment()
        {
            DirectoryInfo? repository = new DirectoryInfo(TestContext.CurrentContext.TestDirectory);
            while (repository != null && !File.Exists(Path.Combine(repository.FullName, "Python_Engine", "Python", "pyproject.toml")))
                repository = repository.Parent;
            repository.Should().NotBeNull("the toolkit sources must be available");
            string source = Path.Combine(repository!.FullName, "Python_Engine", "Python");
            string directory = Path.Combine(EngineQuery.DirectoryEnvironments(), EngineQuery.ToolkitName());

            WithIsolatedDirectory(directory, () =>
            {
                foreach (string file in new[] { "pyproject.toml", "README.md" })
                    File.Copy(Path.Combine(source, file), Path.Combine(directory, file));
                string sourceFolder = Path.Combine(source, "src");
                foreach (string file in Directory.EnumerateFiles(sourceFolder, "*", SearchOption.AllDirectories))
                {
                    string relative = Path.GetRelativePath(sourceFolder, file);
                    if (relative.Split(Path.DirectorySeparatorChar).Contains("__pycache__"))
                        continue;
                    string destination = Path.Combine(directory, "src", relative);
                    Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
                    File.Copy(file, destination);
                }

                try
                {
                    var venv = EngineCompute.InstallPythonToolkitVenv(run: true, reload: false);

                    venv.Should().NotBeNull();
                    venv.Name.Should().Be(EngineQuery.ToolkitName());
                    venv.Executable.Should().Be(Path.Combine(directory, ".venv", "Scripts", "python.exe"));
                    File.Exists(venv.Executable).Should().BeTrue();
                    EngineCompute.RunPythonString(venv,
                        "import importlib.metadata; print(importlib.metadata.version('python_toolkit'))")
                        .Should().Be(BH.Engine.Base.Query.BHoMVersion());
                    File.Exists(Path.Combine(m_Root, "jupyter", "kernels", venv.Name.ToLowerInvariant(), "kernel.json")).Should().BeTrue();
                    EngineCompute.InstallPythonToolkitVenv(run: true, reload: true).Executable.Should().Be(venv.Executable);
                    AssertNoErrors();
                }
                finally
                {
                    string kernel = Path.Combine(m_Root, "jupyter", "kernels", EngineQuery.ToolkitName().ToLowerInvariant(), "kernel.json");
                    if (File.Exists(kernel) && EngineQuery.VirtualEnvironmentExists(EngineQuery.ToolkitName()))
                        EngineCompute.RemoveJupyterKernel(EngineQuery.ToolkitName(), run: true);
                }
            });
        }

        [Test]
        public void InstallUV_InstallsMissingTools()
        {
            PrepareToolPackages();

            EngineCompute.InstallUV(run: true);

            string tools = Run(BH.Engine.Python.Query.UVExecutable(), "tool", "list");
            foreach (string tool in new[] { "ruff", "jupyterlab", "sphinx" })
                tools.Should().Contain(tool + " v1.0.0");
            AssertNoErrors();
        }

        [Test]
        public void InstallUV_SkipsExistingTools()
        {
            PrepareToolPackages();
            EngineCompute.InstallUV(run: true);
            string[] receipts = Directory.GetFiles(Path.Combine(m_Root, "tools"), "uv-receipt.toml", SearchOption.AllDirectories);
            receipts.Should().HaveCount(3);
            var timestamps = receipts.ToDictionary(path => path, File.GetLastWriteTimeUtc);

            EngineCompute.InstallUV(run: true);

            Environment.GetEnvironmentVariable("PATH")!.Split(Path.PathSeparator)[0]
                .Should().Be(BH.Engine.Python.Query.DirectoryTools());
            BH.Engine.Python.Query.UVExecutable().Should()
                .Be(Path.Combine(BH.Engine.Python.Query.DirectoryTools(), "uv.exe"));
            foreach (var receipt in timestamps)
                File.GetLastWriteTimeUtc(receipt.Key).Should().Be(receipt.Value);
            AssertNoErrors();
        }

        [Test]
        public void InstallPackages_SkipsSatisfiedVersion()
        {
            PreparePackageVersions();
            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package==1.0.0" }, run: true);
            string metadata = PackageMetadata("bhom_repeat_package", "1.0.0");
            DateTime timestamp = File.GetLastWriteTimeUtc(metadata);

            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package>=1,<2" }, run: true);

            File.GetLastWriteTimeUtc(metadata).Should().Be(timestamp);
            AssertNoErrors();
        }

        [Test]
        public void InstallPackages_ChangesUnsatisfiedVersion()
        {
            PreparePackageVersions();
            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package==1.0.0" }, run: true);

            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package==2.0.0" }, run: true);

            File.Exists(PackageMetadata("bhom_repeat_package", "2.0.0")).Should().BeTrue();
            File.Exists(PackageMetadata("bhom_repeat_package", "1.0.0")).Should().BeFalse();
            AssertNoErrors();
        }

        [Test]
        public void InstallPackages_RegistersAlreadyInstalledProjectDependency()
        {
            PreparePackageVersions();
            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package==1.0.0" }, run: true);
            string metadata = PackageMetadata("bhom_repeat_package", "1.0.0");
            DateTime timestamp = File.GetLastWriteTimeUtc(metadata);
            CreateProject();

            EngineCompute.InstallPackages(m_Environment, new() { "bhom-repeat-package==1.0.0" }, run: true);

            File.ReadAllText(Path.Combine(m_Root, "pyproject.toml")).Should().Contain("bhom-repeat-package==1.0.0");
            File.GetLastWriteTimeUtc(metadata).Should().Be(timestamp);
            AssertNoErrors();
        }

        [Test]
        public void InstallPackageLocal_SkipsSameUnchangedEditableSource()
        {
            string source = CreateLocalPackage("source with spaces");
            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);
            string metadata = PackageMetadata("bhom_local_package", "1.0.0");
            File.Exists(metadata).Should().BeTrue();
            DateTime timestamp = File.GetLastWriteTimeUtc(metadata);

            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);

            File.GetLastWriteTimeUtc(metadata).Should().Be(timestamp);
            AssertNoErrors();
        }

        [Test]
        public void InstallPackageLocal_ReplacesDifferentEditableSource()
        {
            string first = CreateLocalPackage("first");
            string second = CreateLocalPackage("second");
            EngineCompute.InstallPackageLocal(m_Environment, first, run: true);

            EngineCompute.InstallPackageLocal(m_Environment, second, run: true);

            string directUrl = Path.Combine(Path.GetDirectoryName(PackageMetadata("bhom_local_package", "1.0.0"))!, "direct_url.json");
            File.ReadAllText(directUrl).Should().Contain(new Uri(second + Path.DirectorySeparatorChar).AbsoluteUri.TrimEnd('/'));
            AssertNoErrors();
        }

        [Test]
        public void InstallPackageLocal_UpdatesChangedVersion()
        {
            string source = CreateLocalPackage("local");
            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);
            string project = Path.Combine(source, "pyproject.toml");
            File.WriteAllText(project, File.ReadAllText(project).Replace("1.0.0", "2.0.0"));

            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);

            File.Exists(PackageMetadata("bhom_local_package", "2.0.0")).Should().BeTrue();
            File.Exists(PackageMetadata("bhom_local_package", "1.0.0")).Should().BeFalse();
            AssertNoErrors();
        }

        [Test]
        public void InstallPackageLocal_RegistersProjectDependency()
        {
            string source = CreateLocalPackage("local");
            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);
            CreateProject();

            EngineCompute.InstallPackageLocal(m_Environment, source, run: true);

            File.ReadAllText(Path.Combine(m_Root, "pyproject.toml")).Should().Contain("bhom-local-package");
            AssertNoErrors();
        }

        [Test]
        public void InstallJupyterKernel_SkipsExistingRegistration()
        {
            EngineCompute.InstallJupyterKernel(m_Environment);
            string kernel = Path.Combine(m_Root, "jupyter", "kernels", m_Environment.Name, "kernel.json");
            File.Exists(kernel).Should().BeTrue();
            DateTime timestamp = File.GetLastWriteTimeUtc(kernel);

            EngineCompute.InstallJupyterKernel(m_Environment);

            File.GetLastWriteTimeUtc(kernel).Should().Be(timestamp);
            AssertNoErrors();
        }
    }
}
