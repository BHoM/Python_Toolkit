using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.IO;

namespace BH.Engine.Python
{
    public static partial class Compute
    {
        public static bool InstallPythonToolkit(bool force = false)
        {
            // Install python
            Console.WriteLine("Installing python 3.7 embedded...");
            Compute.Install(force).Wait();

            // Check the installation was successful 
            if (!Query.IsInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Coule not install Python");
                return false;
            }

            // Install pip
            Console.WriteLine("Installing pip...");
            Compute.InstallPip();

            // Check the pip installation was successful 
            if (!Query.IsPipInstalled())
            {
                BH.Engine.Reflection.Compute.RecordError("Could not install pip");
                return false;
            }

            // install project jupyter
            Console.WriteLine("Installing jupyter...");
            Compute.PipInstall("jupyter");
            Compute.PipInstall("jupyterlab");
            Compute.PipInstall("pythonnet");

            return true;
        }

    }
}
