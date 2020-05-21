using System;
using System.Linq;
using BH.Engine.Python;

namespace BH.PostBuild.Python
{
    class Program
    {
        static void Main(string[] args)
        {
            // Parsing arguments
            bool force = false;
            if (args.Contains("--force"))
                force = true;

            // Install python
            Console.WriteLine("Installing python 3.7 embedded...");
            Compute.Install(force).Wait();

            // Check the installation was successful 
            if (!Query.IsInstalled())
                throw new SystemException("Could not install Python");

            // Install pip
            Console.WriteLine("Installing pip...");
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
                throw new SystemException("Could not install pip");

            // install project jupyter
            Console.WriteLine("Installing jupyter...");
            Compute.PipInstall("jupyter");
            Compute.PipInstall("jupyterlab");
            Compute.PipInstall("pythonnet");
        }
    }
}
