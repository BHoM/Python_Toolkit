
using NUnit;
using NUnit.Framework;
using FluentAssertions;

namespace BH.Tests.Engine.Python.Query
{
    public class DirectoryEnvironmentsTests
    {
        [Test]
        public void DirectoryEnvironments()
        {
            string environmentsDirectory = "C:\\ProgramData\\BHoM\\Extensions\\Python";

            var result = new DirectoryInfo(BH.Engine.Python.Query.DirectoryEnvironments());

            Assert.That(result, Is.Not.Null);
            
            result.FullName.Should().Be(environmentsDirectory);

            Directory.Exists(environmentsDirectory).Should().BeTrue();
        }
    }
}