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
using System.IO;
using EngineCompute = BH.Engine.Python.Compute;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python.Compute
{
    [NonParallelizable]
    public class Remove : Base
    {
        [Test]
        public void RemoveKernel_WarnsWhenEnvironmentDoesNotExist()
        {
            EngineCompute.RemoveJupyterKernel(m_Environment.Name + "_missing", run: true);

            AssertWarningWithoutErrors();
        }

        [Test]
        public void RemoveKernel_WarnsWhenKernelDoesNotExist()
        {
            EngineCompute.RemoveJupyterKernel(m_Environment.Name, run: true);

            AssertWarningWithoutErrors();
        }

        [Test]
        public void RemoveKernel_RemovesExistingKernelThenWarnsOnRepeat()
        {
            EngineCompute.InstallJupyterKernel(m_Environment);
            AssertNoErrors();
            BH.Engine.Base.Compute.ClearCurrentEvents();

            EngineCompute.RemoveJupyterKernel(m_Environment.Name, run: true);

            Directory.Exists(Path.Combine(m_Root, "jupyter", "kernels", m_Environment.Name)).Should().BeFalse();
            AssertNoErrors();
            EngineCompute.RemoveJupyterKernel(m_Environment.Name, run: true);
            AssertWarningWithoutErrors();
        }

        [Test]
        public void RemoveVirtualEnvironment_WarnsWhenEnvironmentDoesNotExist()
        {
            EngineCompute.RemoveVirtualEnvironment(m_Environment.Name + "_missing", run: true);

            AssertWarningWithoutErrors();
        }

        [Test]
        public void RemoveVirtualEnvironment_RemovesEnvironmentWithoutKernelThenWarnsOnRepeat()
        {
            EngineCompute.RemoveVirtualEnvironment(m_Environment.Name, run: true);

            Directory.Exists(Path.Combine(m_Root, ".venv")).Should().BeFalse();
            AssertWarningWithoutErrors();
            BH.Engine.Base.Compute.ClearCurrentEvents();
            EngineCompute.RemoveVirtualEnvironment(m_Environment.Name, run: true);
            AssertWarningWithoutErrors();
        }

        [Test]
        public void RemoveUV_WarnsWhenManagedUVDoesNotExist()
        {
            CheckUVRemoval(managedUVExists: false);
        }

        [Test]
        public void RemoveUV_RemovesManagedToolsAndIgnoresExternalUV()
        {
            CheckUVRemoval(managedUVExists: true);
        }

        private void CheckUVRemoval(bool managedUVExists)
        {
            string toolsDirectory = EngineQuery.DirectoryTools();
            string externalDirectory = Path.Combine(m_Root, "external-uv");
            Directory.CreateDirectory(externalDirectory);
            string externalUV = Path.Combine(externalDirectory, "uv.exe");
            File.Copy(EngineQuery.UVExecutable(), externalUV);
            byte[] externalBytes = File.ReadAllBytes(externalUV);
            SetVariable("PATH", externalDirectory + Path.PathSeparator + Environment.GetEnvironmentVariable("PATH"));

            WithIsolatedDirectory(toolsDirectory, () =>
            {
                string marker = Path.Combine(toolsDirectory, "other-tool.txt");
                File.WriteAllText(marker, "preserve when UV is missing");
                if (managedUVExists)
                    File.Copy(externalUV, EngineQuery.UVExecutable());

                EngineCompute.RemoveUV(run: true);

                if (managedUVExists)
                {
                    Directory.Exists(toolsDirectory).Should().BeFalse();
                    AssertNoErrors();
                    BH.Engine.Base.Query.CurrentEvents().Should().BeEmpty();
                }
                else
                {
                    File.Exists(marker).Should().BeTrue();
                    AssertWarningWithoutErrors();
                }
                File.ReadAllBytes(externalUV).Should().Equal(externalBytes);
                Run(externalUV, "--version").Should().StartWith("uv ");
            });
        }
    }
}
