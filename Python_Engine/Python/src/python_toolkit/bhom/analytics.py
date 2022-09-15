import functools
import inspect
import sys
import traceback
from json import dump
from pathlib import Path
from typing import Callable
from uuid import uuid4

from python_toolkit.bhom.encoder import Encoder
from python_toolkit.bhom.ticks import ticks
from python_toolkit.bhom.version import version

ASSEMBLIES_DIR = Path(r"C:\ProgramData\BHoM\Assemblies")
LOGGING_DIR = Path(r"C:\ProgramData\BHoM\Logs")
LOGGING_DIR.mkdir(exist_ok=True, parents=True)


def analytics(f: Callable):
    """A wrapper used to capture usage analytics of the decorated function."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):

        bhom_version = ".".join([str(i) for i in version((ASSEMBLIES_DIR / "BHoM.dll").as_posix())][:2])
        ui_name = "PythonBHoM"
        ticks_value = ticks()
        
        _, module_stack, _, file_path = str(inspect.getmodule(f)).split(" ")
        module_stack = module_stack[1:-1]

        log_file = LOGGING_DIR / f"Usage_{ui_name}_{ticks_value}.log"

        # gather metadata around current callable instance
        d = {
            "BHoMVersion": bhom_version,
            "BHoM_Guid": str(uuid4()),
            "CallerName": f"{module_stack}",
            "ComponentId": "",
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
                "_bhomVersion": bhom_version,
                "_t": "Python"
            },
            "Tags": [],
            "Time":
            {
                "$date": ticks_value
            },
            "UI": ui_name,
            "UiVersion": sys.version,
            "_bhomVersion": bhom_version,
            "_t": "BH.oM.UI.UsageLogEntry"
        }

        # run method and capture errors
        try:
            f(*args, **kwargs)
        except Exception:
            d["Errors"].append(traceback.format_exc())

        with open(log_file, "w+") as fp:
            dump(d, fp, cls=Encoder)
        
        # print function here to enable downstream processes to access the location where the data is stored for loading into BHoM.
        print(log_file, file=sys.stdout)

        return f(*args, **kwargs)

    return wrapper
