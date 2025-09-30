"""Root for the bhom subpackage."""

from pathlib import Path  # pylint: disable=E0401
from os import path
import tempfile
import importlib.metadata

BHOM_LOG_FOLDER = Path(path.expandvars("%PROGRAMDATA%/BHoM/Logs"))
TOOLKIT_NAME = "Python_Toolkit"
BHOM_VERSION = importlib.metadata.version("python_toolkit")

if not BHOM_LOG_FOLDER.exists():
    BHOM_LOG_FOLDER = Path(tempfile.gettempdir()) / "BHoM" / "Logs"
    BHOM_LOG_FOLDER.mkdir(exist_ok=True, parents=True)