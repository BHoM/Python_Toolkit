using System;
using BH.Engine.Python;

namespace BH.PostBuild.Python
{
    class Program
    {
        static void Main(string[] args)
        {
            // Install python
            Compute.Install().Wait();

            // Check the installation was successful 
            if (!Query.IsInstalled())
                throw new SystemException("Could not install Python");

            // Install pip
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
                throw new SystemException("Could not install pip");

            // Install most commonly used ml packages

            if (args.Length <= 0 || !bool.Parse(args[0]))
                return;

            // Pillow
            Compute.PipInstall("pillow");

            // numpy
            Compute.PipInstall("numpy");

            // tensorflow
            Compute.PipInstall("tensorflow", "2.0");

            // pytorch
            Compute.PipInstall("torch===1.4.0 torchvision===0.5.0 -f https://download.pytorch.org/whl/torch_stable.html");

            //scikit learn
        }
    }
}
