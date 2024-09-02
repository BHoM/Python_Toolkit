"""Root for the bhom subpackage."""

from pathlib import Path  # pylint: disable=E0401
from os import path

from win32api import HIWORD, LOWORD, GetFileVersionInfo

BHOM_ASSEMBLIES_DIRECTORY = Path(path.expandvars("%PROGRAMDATA%/BHoM/Assemblies"))
BHOM_LOG_FOLDER = Path(path.expandvars("%PROGRAMDATA%/BHoM/Logs"))
TOOLKIT_NAME = "Python_Toolkit"

if not BHOM_LOG_FOLDER.exists():
    BHOM_LOG_FOLDER = Path(path.expandvars("%TEMP%/BHoMLogs"))
    BHOM_LOG_FOLDER.mkdir(exist_ok=True)

if not BHOM_ASSEMBLIES_DIRECTORY.exists():
    BHOM_VERSION = ""
else:
    _file_version_ms = GetFileVersionInfo(
        (BHOM_ASSEMBLIES_DIRECTORY / "BHoM.dll").as_posix(), "\\"
    )["FileVersionMS"]

    BHOM_VERSION = f"{HIWORD(_file_version_ms)}.{LOWORD(_file_version_ms)}"
