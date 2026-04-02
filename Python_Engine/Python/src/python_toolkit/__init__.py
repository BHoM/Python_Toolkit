"""Base module for the python_toolkit package."""
# pylint: disable=E0401
import getpass
import os
from pathlib import Path

import matplotlib.pyplot as plt

# pylint: disable=E0401

# get common paths
DATA_DIRECTORY = (Path(__file__).parent.parent / "data").absolute()
BHOM_DIRECTORY = (Path(__file__).parent / "bhom").absolute()
HOME_DIRECTORY = (Path("C:/Users/") / getpass.getuser()).absolute()

TOOLKIT_NAME = "Python_Toolkit"

if os.name == "nt":
    # override "HOME" in case this is set to something other than default for windows
    os.environ["HOME"] = (Path("C:/Users/") / getpass.getuser()).as_posix()
