
using NUnit;
using NUnit.Framework;
using FluentAssertions;
using BH.oM.Python;

namespace BH.Tests.Engine.Python.Compute
{
    public class VirtualEnvironmentTests
    {
        [Test]
        public void VirtualEnvironment_FromTOML()
        {
            string envName = "test_from_toml";
            string envDirectory = BH.Engine.Python.Query.DirectoryEnvironments();

            // pre-run clean-up
            try
            {
                BH.Engine.Python.Compute.RemoveVirtualEnvironment(name: envName, true);
            }
            catch {
                // do it the manual way, if there is no env to remove, it'll throw an error
                Directory.Delete(path: Path.Combine(envDirectory, envName), recursive: true);
            }

            // create the test directory
            string testDirectory = Path.Combine(envDirectory, envName);
            Directory.CreateDirectory(testDirectory);

            // create dummy README file
            File.WriteAllText(Path.Combine(testDirectory, "README.md"), "");

            // create dummy TOML file
            List<string> lines =
            [
                "[project]",
                $"name = \"{envName}\"",
                "version = \"0.1.0\"",
                "description = \"A test environment.\"",
                "readme = \"README.md\"",
                "requires-python = \">=3.10,<3.11\"",
                "authors = [",
                "    { name = \"BHoM\", email = \"bhombot@burohappold.com\" }",
                "]",
                "dependencies = [\"matplotlib\"]",
                "[build-system]",
                "requires = [\"hatchling\"]",
                "build-backend = \"hatchling.build\"",
                "",
                "[dependency-groups]",
                "dev = [\"ipykernel\", \"ruff\"]",
                "[tool.hatch.build.targets.wheel]",
                $"packages = [\"src/{envName}\"]"
            ];

            string tomlFileContent = string.Join(Environment.NewLine, lines);
            string tomlFile = Path.Combine(testDirectory, "pyproject.toml");
            File.WriteAllText(tomlFile, tomlFileContent);

            // create a dummy Python package
            string packageDir = Path.Combine(testDirectory, "src", envName);
            Directory.CreateDirectory(packageDir);
            File.WriteAllText(Path.Combine(packageDir, "__init__.py"), "");
            
            // run the method
            PythonEnvironment venv = BH.Engine.Python.Compute.VirtualEnvironment(tomlFile: tomlFile, reload: false);

            // ensure that ipykernel is installed
            string result = BH.Engine.Python.Compute.RunPythonString(venv: venv, "import ipykernel");
            result.ToLower().Should().NotContainAny(["error", "exception"]);

            // assert that the virtual environment was created correctly
            venv.Should().NotBeNull();
            venv.Name.Should().Be(envName);
            File.Exists(venv.Executable).Should().BeTrue();

            // run again, reloading this time
            PythonEnvironment reloadedVenv = BH.Engine.Python.Compute.VirtualEnvironment(tomlFile: tomlFile, reload: true);

            // assert that the virtual environment was created correctly
            reloadedVenv.Should().NotBeNull();
            reloadedVenv.Name.Should().Be(envName);
            reloadedVenv.Executable.Should().Be(Path.Combine(testDirectory, ".venv", "Scripts", "python.exe"));
            File.Exists(reloadedVenv.Executable).Should().BeTrue();

            // clean-up
            BH.Engine.Python.Compute.RemoveVirtualEnvironment(name: envName, true);
        }

        [Test]
        public void VirtualEnvironment_FromTargetVersion()
        {
            string targetVersion = "3.11";
            string envName = "test_from_target_version";
            string envDirectory = BH.Engine.Python.Query.DirectoryEnvironments();

            // pre-run clean-up
            try
            {
                BH.Engine.Python.Compute.RemoveVirtualEnvironment(name: envName, true);
            }
            catch
            {
                // do it the manual way, if there is no env to remove, it'll throw an error
                Directory.Delete(path: Path.Combine(envDirectory, envName), recursive: true);
            }

            // run the method
            PythonEnvironment venv = BH.Engine.Python.Compute.VirtualEnvironment(version: targetVersion, name: envName, reload: false);

            // add a package
            BH.Engine.Python.Compute.InstallPackages(venv, ["matplotlib"], true);

            // ensure that ipykernel is installed
            string result = BH.Engine.Python.Compute.RunPythonString(venv: venv, "import ipykernel;import matplotlib");
            result.ToLower().Should().NotContainAny(["error", "exception"]);

            // assert that the virtual environment was created correctly
            venv.Should().NotBeNull();
            venv.Name.Should().Be(envName);
            File.Exists(venv.Executable).Should().BeTrue();

            // run again, reloading this time
            PythonEnvironment reloadedVenv = BH.Engine.Python.Compute.VirtualEnvironment(version: targetVersion, name: envName, reload: true);

            // assert that the virtual environment was created correctly
            reloadedVenv.Should().NotBeNull();
            reloadedVenv.Name.Should().Be(envName);
            reloadedVenv.Executable.Should().Be(Path.Combine(envDirectory, envName,  ".venv", "Scripts", "python.exe"));
            File.Exists(reloadedVenv.Executable).Should().BeTrue();

            // clean-up
            BH.Engine.Python.Compute.RemoveVirtualEnvironment(name: envName, true);
        }
    }
}