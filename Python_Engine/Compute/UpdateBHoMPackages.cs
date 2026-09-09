using BH.oM.Base.Attributes;
using BH.oM.Python;
using BH.oM.Python.Enums;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Text;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        [Description("Using the environment name (and version if the environment name is the base python environment), directly install/update missing BHoM packages.")]
        [Input("environmentName", "The name of the environment to update.")]
        [Input("version", "If the environment name is the name of the base python environment, the version that needs updating.")]
        public static void UpdateBHoMPackages(this string environmentName, PythonVersion version = PythonVersion.Undefined)
        {
            //construct the expected PythonEnvironment and pass to UpdateBHoMPackages
            PythonEnvironment env = new PythonEnvironment()
            {
                Name = environmentName,
            };

            //python version is only used if the environment name is this toolkits name.
            if (environmentName == Query.ToolkitName())
            {
                if (version == PythonVersion.Undefined)
                {
                    BH.Engine.Base.Compute.RecordError("The version must be specified when updating BHoM packages for a base python environment. No updates have occurred.");
                    return;
                }

                env.Executable = Path.Combine(Query.DirectoryBaseEnvironment(version), "python.exe");
            }
            else
                env.Executable = Query.VirtualEnvironmentExecutable(environmentName);

            UpdateBHoMPackages(env);
        }

        /***************************************************/

        [Description("Using a PythonEnvironment, directly install/update missing BHoM packages.")]
        [Input("environment", "The python environment to update.")]
        public static void UpdateBHoMPackages(this PythonEnvironment environment)
        {
            if (!Query.VirtualEnvironmentExists(environment.Name))
            {
                BH.Engine.Base.Compute.RecordError("Given environment does not exist.");
                return;
            }

            string localPackageDirectory = ResolvePackageDirectory(environment);

            if (!Directory.Exists(localPackageDirectory))
            {
                BH.Engine.Base.Compute.RecordError($"There is no local package directory for {environment.Name} (searched at \"{localPackageDirectory}\"). No packages were updated.");
                return;
            }

            InstallPackageLocal(environment, localPackageDirectory);
        }

        /***************************************************/

        private static string ResolvePackageDirectory(PythonEnvironment environment)
        {
            string packageName = environment.Name;
            string codeDirectory = Query.DirectoryCode();
            return Path.Combine(codeDirectory, packageName);
        }
    }
}