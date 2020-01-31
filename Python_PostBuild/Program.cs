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
            Compute.Install(force).Wait();

            // Check the installation was successful 
            if (!Query.IsInstalled())
                throw new SystemException("Could not install Python");

            // Install pip
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
                throw new SystemException("Could not install pip");

            // Install most commonly used ml packages
            foreach(string module in args)
            {
                if (module.Contains("--force"))
                    continue;

                try
                {
                    Compute.PipInstall(module);
                }
                catch { }
            }
        }
    }
}
