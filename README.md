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
1. Open ai UI of your choice (e.g. Grasshopper)
1. Run the `InstallPythonToolkit` component and wait for the installation to finish.
1. he installation has succeeded if the packages installed are:
	  - Python 3.7
  	- jupyter
  	- matplotlib
  	- Python_Toolkit
1. Restart your UI

To check that all went ok you can run the component `BH.Engine.Python.Compute.Import` with input a string `Python_Toolkit`,
and check that it succeed without errors

## Building the BHoM and the Toolkits from Source ##
You will need the following to build BHoM:

- Microsoft Visual Studio 2013 or higher
- Microsoft .NET Framework 4.0 and above (included with Visual Studio 2013)
- Note that there are no software - specific dependencies (only operating system relevant), this is specific: BHoM is a software agnostic object model.


## Want to contribute? ##

BHoM is an open-source project and would be nothing without its community. Take a look at our contributing guidelines and tips [here](https://github.com/BHoM/BHoM/blob/master/CONTRIBUTING.md).


## Licence ##

BHoM is free software licenced under GNU Lesser General Public Licence - [https://www.gnu.org/licenses/lgpl-3.0.html](https://www.gnu.org/licenses/lgpl-3.0.html)  
Each contributor holds copyright over their respective contributions.
The project versioning (Git) records all such contribution source information.
See [LICENSE](https://github.com/BHoM/BHoM/blob/master/LICENSE) and [COPYRIGHT_HEADER](https://github.com/BHoM/BHoM/blob/master/COPYRIGHT_HEADER.txt).
