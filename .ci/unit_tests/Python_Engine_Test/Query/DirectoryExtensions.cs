
using NUnit;
using NUnit.Framework;
using FluentAssertions;

namespace BH.Tests.Engine.Python.Query
{
    public class DirectoryExtensionTests
    {
        [Test]
        public void DirectoryExtension()
        {
            string extensionsDirectory = "C:\\ProgramData\\BHoM\\Extensions";

            var result = new DirectoryInfo(BH.Engine.Python.Query.DirectoryExtensions());

            Assert.That(result, Is.Not.Null);
            
            result.FullName.Should().Be(extensionsDirectory);

            Directory.Exists(extensionsDirectory).Should().BeTrue();
        }
    }
}