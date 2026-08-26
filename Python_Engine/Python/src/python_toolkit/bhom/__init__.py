"""Root for the bhom subpackage."""

import os
from pathlib import Path  # pylint: disable=E0401
from os import path
import tempfile
import importlib.metadata

if os.name == 'nt':
    from .installer_info import INSTALLER_INFO
else:
    INSTALLER_INFO = {"Version": importlib.metadata.version("python_toolkit")}

BHOM_LOG_FOLDER = Path(path.expandvars("%PROGRAMDATA%/BHoM/Logs"))
TEMP_LOG_FOLDER = Path(tempfile.gettempdir()) / "BHoM" / "Logs"
TOOLKIT_NAME = "Python_Toolkit"
BHOM_VERSION = INSTALLER_INFO["Version"]

#Environment variable that if set disables BHoM analytics logging.
DISABLE_ANALYTICS = os.environ.get("DISABLE_BHOM_ANALYTICS", None)
if DISABLE_ANALYTICS is None:
    DISABLE_ANALYTICS = False
else:
    DISABLE_ANALYTICS = True

if not BHOM_LOG_FOLDER.exists():

    try:
        BHOM_LOG_FOLDER.mkdir(exist_ok=True, parents=True)

        #migration recovery for any logs in the temp folder
        if TEMP_LOG_FOLDER.exists():
            for file in TEMP_LOG_FOLDER.glob("*.log"):
                file.rename(BHOM_LOG_FOLDER / file.name)

    except Exception as e:
        BHOM_LOG_FOLDER = TEMP_LOG_FOLDER
        BHOM_LOG_FOLDER.mkdir(exist_ok=True, parents=True)



