[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
## Install me
To install the Python_Toolkit:
1. Compile:  
    1. [BHoM](https://github.com/BHoM/BHoM)  
    1. [BHoM_Engine](https://github.com/BHoM/BHoM_Engine)  
    1. [BHoM_Adapter](https://github.com/BHoM/BHoM_Adapter)   
    1. [BHoM_UI](https://github.com/BHoM/BHoM_UI)  
    1. [Rhinoceros_Toolkit](https://github.com/BHoM/Rhinoceros_Toolkit) 
    1. [Grasshopper_Toolkit](https://github.com/BHoM/Grasshopper_Toolkit)  
    1. Python_Toolkit (this repo)
1. Open a UI of your choice (e.g. Grasshopper)
1. Run the `BH.Engine.Python.Compute.InstallPythonToolkit` component and wait for the installation to finish
1. The installation has succeeded if the install packages include:
	- Python 3.7
  	- jupyterlab
  	- matplotlib
  	- Python_Toolkit
1. Restart your UI or recompute the script

To check whether all went well you can run the component `BH.Engine.Python.Compute.Import` with an input of a string as `Python_Engine`,
and check that it succeed without errors

## Installation structure
There are two main events to install the toolkit:
1. Compiling the toolkit. This does two things:
	- It builds the dynamic libraries required by .NET and copies them to C:\ProgramData\BHoM\Assemblies
	- It packs the python files in the toolkit and copies them to C:\ProgramData\BHoM\Extensions\Python\src
2. Installing the Toolkit from the UI. This is performed by running the `InstallPythonToolkit` method. This will:
	- Download Python and install python
	- Download and install `pip`
	- Install the necessary packages (e.g. `jupyterlab`)
	- Install the python bindings of the Python_Toolkit from C:\ProgramData\BHoM\Extensions\Python\src
	  This contains all the code that is currently developed in the toolkit in python

## Building the BHoM and the Toolkits from Source ##
You will need the following to build BHoM:

- Microsoft Visual Studio 2013 or higher
- Microsoft .NET Framework 4.0 and above (included with Visual Studio 2013)
- Note that there are no software - specific dependencies (only operating system relevant), this is specific: BHoM is a software agnostic object model.

## Running commands and creating environments

UV is installed at `Path.Combine(Query.DirectoryTools(), "uv.exe")`. Engine methods, tests, and PowerShell scripts invoke this BHoM-managed executable directly, never an unrelated UV on PATH. Installation prepends the tools directory to the current process PATH without changing the user or system PATH.

`RunCommandStdout` returns `BH.oM.Base.Output<string, string, int>`: `Item1` is stdout, `Item2` is stderr, and `Item3` is the exit code (zero for success, -1 for timeout). Both streams are retained on success, failure, and timeout. Callers that previously consumed a string must select the appropriate output. Command failures are also recorded as BHoM errors; invalid working directories and process-start failures still throw.

Creating an environment from a TOML file updates its static `[project].version` to `BH.Engine.Base.Query.BHoMVersion()` before installation. Other version fields are left unchanged. Recreating that environment preserves the TOML file and package sources.

## Want to contribute? ##

BHoM is an open-source project and would be nothing without its community. Take a look at our contributing guidelines and tips [here](https://github.com/BHoM/BHoM/blob/main/CONTRIBUTING.md).


## Licence ##

BHoM is free software licenced under GNU Lesser General Public Licence - [https://www.gnu.org/licenses/lgpl-3.0.html](https://www.gnu.org/licenses/lgpl-3.0.html)  
Each contributor holds copyright over their respective contributions.
The project versioning (Git) records all such contribution source information.
See [LICENSE](https://github.com/BHoM/BHoM/blob/main/LICENSE) and [COPYRIGHT_HEADER](https://github.com/BHoM/BHoM/blob/main/COPYRIGHT_HEADER.txt).
