"""Root for the bhom subpackage."""

import os
from pathlib import Path  # pylint: disable=E0401
from os import path
import tempfile
import importlib.metadata

BHOM_LOG_FOLDER = Path(path.expandvars("%PROGRAMDATA%/BHoM/Logs"))
TOOLKIT_NAME = "Python_Toolkit"
BHOM_VERSION = importlib.metadata.version("python_toolkit")

#Environment variable that if set disables BHoM analytics logging.
DISABLE_ANALYTICS = os.environ.get("DISABLE_BHOM_ANALYTICS", None)
if DISABLE_ANALYTICS is None:
    DISABLE_ANALYTICS = False
else:
    DISABLE_ANALYTICS = True

if not BHOM_LOG_FOLDER.exists():

    try:
        BHOM_LOG_FOLDER.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        BHOM_LOG_FOLDER = Path(tempfile.gettempdir()) / "BHoM" / "Logs"
        BHOM_LOG_FOLDER.mkdir(exist_ok=True, parents=True)


#migration recovery for any logs in the temp folder
old_temp_log = Path(tempfile.gettempdir()) / "BHoM" / "Logs"
if old_temp_log.exists():
    for file in old_temp_log.glob("*.log"):
        file.rename(BHOM_LOG_FOLDER / file.name)