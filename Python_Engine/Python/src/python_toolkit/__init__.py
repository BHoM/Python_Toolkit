"""Base module for the python_toolkit package."""

import os
from pathlib import Path

TOOLKIT_NAME = "Python_Toolkit"

if os.name == "nt":
    # override "HOME" in case this is set to something other than default for windows
    os.environ["HOME"] = Path.home().as_posix()

ASSETS_DIRECTORY = (Path(__file__).parents[2] / "assets").absolute()
