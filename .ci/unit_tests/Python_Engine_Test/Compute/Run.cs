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
using FluentAssertions;
using System.Diagnostics;
using System.Text.RegularExpressions;
using EngineCompute = BH.Engine.Python.Compute;
using EngineQuery = BH.Engine.Python.Query;

namespace BH.Tests.Engine.Python.Compute
{
    [NonParallelizable]
    public class Run
    {
        [SetUp]
        [TearDown]
        public void CleanUp()
        {
            BH.Engine.Base.Compute.ClearCurrentEvents();
        }

        [TestCase(0)]
        [TestCase(7)]
        public void RunCommandStdout_ReturnsBothStreamsAndExitCode(int exitCode)
        {
            SynchronizationContext? original = SynchronizationContext.Current;
            try
            {
                SynchronizationContext.SetSynchronizationContext(new NonPumpingContext());
                var result = EngineCompute.RunCommandStdout(
                    $"(for /L %i in (1,1,2000) do @(echo output& echo diagnostic 1>&2)) & exit /b {exitCode}");

                result.Should().NotBeNull("failed commands must still return both streams and their exit code");
                result.Item1.Split('\n').Should().HaveCount(2000);
                result.Item2.Split('\n').Should().HaveCount(2000);
                result.Item1.Should().StartWith("output").And.EndWith("output");
                result.Item2.Should().StartWith("diagnostic").And.EndWith("diagnostic");
                result.Item3.Should().Be(exitCode);
                BH.Engine.Base.Query.CurrentEvents().Any(e => e.Type == EventType.Error).Should().Be(exitCode != 0);
            }
            finally
            {
                SynchronizationContext.SetSynchronizationContext(original);
            }
        }

        [Test]
        public void RunCommandStdout_TimeoutRetainsBothStreams()
        {
            Stopwatch timer = Stopwatch.StartNew();
            var result = EngineCompute.RunCommandStdout(
                "echo started & echo diagnostic 1>&2 & powershell.exe -NoProfile -NonInteractive -Command \"Start-Sleep -Seconds 30\"",
                timeoutMinutes: 0.02);

            result.Should().NotBeNull("timeouts must still return captured streams and exit code -1");
            result.Item1.Should().Be("started");
            result.Item2.Should().Be("diagnostic");
            result.Item3.Should().Be(-1);
            timer.Elapsed.Should().BeLessThan(TimeSpan.FromSeconds(10));
            BH.Engine.Base.Query.CurrentEvents().Should().Contain(e => e.Type == EventType.Error && e.Message.Contains("timeout"));
        }

        private sealed class NonPumpingContext : SynchronizationContext
        {
            public override void Post(SendOrPostCallback callback, object? state)
            {
                throw new InvalidOperationException("The command runner captured the host synchronization context.");
            }
        }
    }
}
