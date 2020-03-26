using System;
using System.IO;
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

            // install pytohn side of python_toolkit 
            Console.WriteLine("Installing python_toolkit in python...");
            Compute.PipInstall("-e git+https://github.com/BHoM/Python_Toolkit.git@MachineLearning#56-PythonFramework");

            // install pytorch
            Console.WriteLine("Installing pytorch");
            Compute.PipInstall("torch", version: "1.4.0", findLinks: "https://download.pytorch.org/whl/torch_stable.html");
            Compute.PipInstall("torchvision", version: "0.5.0", findLinks: "https://download.pytorch.org/whl/torch_stable.html");

            // Install most commonly used ml packages
            foreach (string module in args)
            {
                try
                {
                    Console.WriteLine($"Installing {module}...");
                    Compute.PipInstall(module, force: force);
                }
                catch { }
            }
        }
    }
}
