# Python_Toolkit

The code contained here is intended to be used in conjunction with the Python_Toolkit, as part of a wider [BHoM](https://bhom.xyz/) installation. Its main purpose is to augment capabilities of the BHoM.

# BHoM Python environments

_Where guidelines are not explicitly given, code style standards and procedures should refer to the wider [BHoM code compliance guidance](https://github.com/BHoM/documentation/wiki/Code-Compliance)._

## Creation of a Python environment

A BHoM toolkit can be associated with a Python environment. The toolkit needs to have a location where Python code associated with that toolkit exists - so the first step is in creating that location and structure.

**In the example below we'll go through creating a Python environment for the `Example_Toolkit`**.

### Creating the Python code structure

All Python code within BHoM should be placed within the hosting toolkit, inside its `*_Engine` folder. Within this folder, the following directory structure should be created (files have been included here within `./example_toolkit` and `./tests` also, though these are purely indicative):

```
.
├── ...
├── Example_Engine
│   └── Python
|       ├── README.md
|       ├── setup.py
|       ├── requirements.txt
|       └── src
|           ├── example_toolkit
|           |   ├── __init__.py
|           |   ├── code_directory_a
|           |   |   ├── __init__.py__
|           |   |   └── method.py
|           |   ├── code_directory_b
|           |   |   └── __init__.py
|           |   |   └── method.py
|           |   └── helpers
|           |       ├── __init__.py
|           |       └── helper_method_a.py
|           └── tests
|               ├── __init__.py
|               ├── test_code_directory_a
|               ├── test_code_directory_b
|               └── test_helpers
└── ...
```

### Populating the `requirements.txt` file content

If you've used Python before you'll be familiar with requirements.txt files. These contain the packages required by a given Python environment, and can specify the version of those packages also. In BHoM, and environment may be used within a specific toolkit, or it could reference an external Python environment (replicating it for modification according to BHoM requirements), or even as a standalone environment used for a specific purpose or project.

Toolkit-specific environments, and standalone environments should be explicit about which versions of packages to install.

If the Python environment created is referencing an external environment (i.e. it recreates the external environment for use/development in BHoM) then packages listed in the `requirements.txt` file should not state versions. This is so that the external "source" environment has control over packages installed, rather than the BHoM copy of that environment.

By default, `ipykernel` is included in all BHoM create Python environments in order to use that environments Python kernel within a [Jupyter Notebook](https://jupyter.org/) UI. `pytest` is also installed to aid in automated unit testing, and `pylint` is included to aid in finding errors in code during development.

### Populating the `setup.py` file

All BHoM Python code should be stored within the `./Python/src/example_toolkit` directory, and can be further organised within this to split different packages up to better manage code. The `setup.py` file defines what folders to include when installing this code into the environment that will be created. In the code below, `src` is set as the location where the Python code is stored, and `requirements.txt` is also being used to state what packages to install alongside the local code.

```python
## setup.py ##
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = [i.strip() for i in (here / "requirements.txt").read_text(encoding="utf-8-sig").splitlines()]

setup(
    name="example_toolkit",
    author="BHoM",
    author_email="bhombot@burohappold.com",
    description="A Python library that enables Example Toolkit python code to be used within BHoM workflows.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BHoM/Example_Toolkit",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=['tests']),
    install_requires=requirements,
)
```

### Installing the Python environment

Once the Example_Toolkit has been given a Python folder containing the requisite files and directory structure, two methods are required in the toolkit to which Python code is being added. The first is a `Query` method for the name of that toolkit:

```C#
using BH.oM.Base.Attributes;

using System.ComponentModel;

namespace BH.Engine.Example
{
    public static partial class Query
    {
        [Description("Get the name of the current toolkit.")]
        [Output("name", "The name of the current toolkit.")]
        public static string ToolkitName()
        {
            return "Example_Toolkit";
        }
    }
}
```

And the second is a `Compute` method called `ExampleToolkitPythonEnvironment` which installs the toolkits associated Python environment. In the method below, Python v3.7.9 is being used for this toolkits Python environment:

```C#
using BH.oM.Base.Attributes;
using BH.oM.Python;

using System.ComponentModel;

namespace BH.Engine.Example
{
    public static partial class Compute
    {
        [Description("Install the Python virtualenv for the Example_Toolkit.")]
        [Input("run", "Run the installation process for this BHoM Python environment.")]
        [Output("env", "The Example_Toolkit Python environment, including any locally referenced BHoM code.")]
        public static PythonEnvironment ExampleToolkitPythonEnvironment(bool run = false)
        {
            if (run)
            {
                return BH.Engine.Python.Compute.InstallVirtualenv(
                    name: Query.ToolkitName(),
                    pythonVersion: BH.oM.Python.Enums.PythonVersion.v3_7_9,  // the version of Python to be used for this toolkits Python environment
                    localPackage: Path.Combine(Engine.Python.Query.CodeDirectory(), Query.ToolkitName()),
                    run: run
                );
            }
            return null;
        }
    }
}
```

Variations upon this can be made to reference external environments with known Python versions and installed packages also - with the [LadybugTools_Toolkit](https://github.com/BHoM/LadybugTools_Toolkit/blob/c005dc901459c4b779b329b65406d4a6c88f0965/LadybugTools_Engine/Compute/LadybugToolsToolkitPythonEnvironment.cs) showing how this is done.

## Structure of Python code

Unless otherwise specified, code style must follow guidance from [PEP8](https://peps.python.org/pep-0008/), unless otherwise stated in this document or in [BHoM C# guidance](https://github.com/BHoM/documentation/wiki/Coding-Style) (though some aspects of C# guidance are not applicable here due to differences between the two languages).

### BHoM/Python specific style guidance

- One method or class per file.
- As much as possible, your code should be logically organised into a collection of directories and subdirectories.
- Helper methods often don't fit into specific workflows and exist outside of packaged Python modules. These should be placed in a `./helpers` directory in the root of the toolkits Python code.
- Files named in snake_case. For example, a class called `AThing`, would be in a file called `a_thing.py`, and a method called `do_stuff` would be in a files called `do_stuff.py`.
- Imports at the top of files must be absolute, to remove all ambiguity.
- Type hints are required on all functions and classes (both inputs and outputs).
- Docstrings must be added for all classes and methods. If the method is wrapped by a class, then only a description of that method is required as a minimum (unless the method is a dunder method).
- Docstrings should be provided in [Google format](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods).
- Default values should only be used where the defaults given are expected by a typical user of that code. If in doubt do not include a default.
- Where defaults are given, these are best placed in the method/class instantiation rather than reassigning to that variable upon checking if variable "is None" later in the code.
- Errors should be handled gracefully. When errors happen, the user should be told what went wrong and how to fix it. Broad Exceptions are allowed, although specific errors are preferable. Errors should also be captured at the lowest-possible level.

## Testing

The following guidelines are given for implementation of Python code testing. It is anticipated that the majority of testing can be undertaken automatically without need for human interaction. This does increase the time required to develop code - but will result in far better code overall as a result. Everything that can be reasonably tested should be done so. Dispensation may be given from the CI/CD lead where appropriate following suitable justification made by the code developer.

The testing framework used in all BHoM Python code is `pytest`. In each BHoM Python code directory there exists a `./src` folder (containing the code), and a `./tests` folder containing related tests. Tests should be created by the person that writes the code that is being tested, and subject to review by those undertaking the PR review. A passing unit test is required for PR approval. The reviewer needs to ensure that the testing procedure is sufficiently comprehensive as part of their approval.

An example is given below for an appropriate candidate for testing:

```python
## example_code.py ##
from typing import Union
def add(a: Union[int, float], b: Union[int, float]) -> float:
    """Add two numbers together.

    Args:
        a (Union[int, float]): The first number.
        b (Union[int, float]): The second number.

    Returns:
        Union[int, float]: The result of adding the inputs together.
    """
    if (not isinstance(a, (int, float))) and (not isinstance(b, (int, float)):
        raise TypeError(f"The combination of dtypes ({type(a)}, {type(b)}) passed are not valid for this method.")
    return a + b
```

... with testing procedures defined to check that this method works as expected ...

```python
## test_example_code.py ##
import pytest
from example_code import add

def test_add():
    a = 1.5
    b = 2.5
    assert add(a, b) == 4.0

def test_add_fails():
    with pytest.raises(TypeError) as e_info:
        add("1", 1)

```

... and the command used to test this would be ...

```
python -m pytest ./test_example_code.py
```

Tests should be written so that:

- Cases where a method runs correctly and returns a pre-defined result pass.
- Cases where the method handles errors gracefully and raises an expected error pass.
- In complex processes, tests may not be possible for all methods; however, it is expected that the lowest methods in that process are tested to reduce risk of error cascading through these processes.
- In complex processes that rely on external programs, assertions should be made at the beginning of testing that those programs are available to the testing methods.
- Where stochastic results are expected, use "fuzzy matching" to check for closeness of results (see [pytest.approx](https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest-approx))

# Recommended development environment

Python in the context of BHoM is intended to be used where C# may not be as rapid or best placed to give results. As such, it can be considered more of a "scripting" language - with scope for formalisation into properly formatted and discretised code as part of BHoM toolkits. Ultimately it is up to the developer how to write their code, but the following setup is suggested for those just starting.

## IDE

Use VSCode for Python code development. This editor provides extensibility via packages which enable the automation of a lot of repetitive actions. The plugins that are recommended are:

- python
- pylance
- Prettier
- autoDocstring

Additionally, the following user settings can be added to enable auto-formatting of code upon saving to PEP8 compliance using "black" (a requirement of all BHoM Python code).

```json
{
  "python.formatting.provider": "black",
  "python.defaultInterpreterPath": "C:/ProgramData/BHoM/Extensions/PythonEnvironments/Example_Toolkit/python.exe",
  "editor.formatOnType": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": true,
    "source.organizeImports": true,
    "source.sortMembers": true
  },
  "python.formatting.blackPath": "C:/ProgramData/BHoM/Extensions/PythonEnvironments/Python_Toolkit/Scripts/black.exe",
  "python.linting.pylintArgs": ["--disable=C0114"]
}
```

## Scripting/notebooks

Jupyter notebooks provide a good testing environment for Python code development. The registered ipykernel associated with each BHoM Python environment enables creation of environment specific notebooks with access to all code contained therein. During development it can be useful to reload changes in code rather than restarting teh kernel each time you modify the source code. To do this, include the following in the first cell in a notebook and changes you make in the referenced \*.py files will be brought through into the notebook environment.

```python
%load_ext autoreload
%autoreload 2
```
