import functools
import inspect
import sys
import traceback
from pathlib import Path
from typing import Callable
from uuid import uuid4

from python_toolkit.bhom.encoder import Encoder
from python_toolkit.bhom.ticks import ticks
from python_toolkit.bhom.version import version

ASSEMBLIES_DIR = Path(r"C:\ProgramData\BHoM\Assemblies")
LOGGING_DIR = Path(r"C:\ProgramData\BHoM\Logs")
LOGGING_DIR.mkdir(exist_ok=True, parents=True)
BHOM_VERSION = ".".join([str(i) for i in version((ASSEMBLIES_DIR / "BHoM.dll").as_posix())][:2])
UI_NAME = "PythonBHoM"
TICKS = ticks()


def analytics(f: Callable):
    """A wrapper used to capture usage analytics of the decorated function."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        
        _, module_stack, _, file_path = str(inspect.getmodule(f)).split(" ")
        module_stack = module_stack[1:-1]

        log_file = LOGGING_DIR / f"Usage_{UI_NAME}_{TICKS}.log"

        # gather metadata around current callable instance
        d = {
            "BHoMVersion": BHOM_VERSION,
            "BHoM_Guid": str(uuid4()),
            "CallerName": f"{module_stack}",
            "ComponentId": str(uuid4()),
            "CustomData": {},
            "Errors": [],
            "FileId": "",
            "FileName": "",
            "Fragments": [],
            "Name": "",
            "ProjectID": "",
            "SelectedItem":
            {
                "Name": f.__name__,
                "_bhomVersion": BHOM_VERSION,
                "_t": "Python"
            },
            "Tags": [],
            "Time":
            {
                "$date": TICKS
            },
            "UI": UI_NAME,
            "UiVersion": sys.version,
            "_bhomVersion": BHOM_VERSION,
            "_t": "BH.oM.UI.UsageLogEntry"
        }

        # run method and capture errors
        try:
            f(*args, **kwargs)
        except Exception:
            d["Errors"].append(traceback.format_exc())

        with open(log_file, "a+") as fp:
            fp.write(str(d) + "\n")
        
        # print function here to enable downstream processes to access the location where the data is stored for loading into BHoM.
        #print(log_file, file=sys.stdout)

        return f(*args, **kwargs)

    return wrapper
