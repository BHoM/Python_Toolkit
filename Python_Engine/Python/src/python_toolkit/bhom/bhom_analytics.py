import functools
import inspect
import socket
import sys
import traceback
from datetime import datetime
from json import dump
from pathlib import Path
from typing import Callable
from uuid import uuid4

from python_toolkit.bhom.bhom_json_encoder import BHoMJSONEncoder


def bhom_analytics(f: Callable):
    """A wrapper used to capture usage analytics of the decorated function."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        output_file = Path(f"C:/Temp/bhom_python_{uuid4()}.json")
        d = {
            "StartTime": datetime.now(),
            "Computer": socket.gethostname(),
            "FileName": Path(inspect.getfile(f)).as_posix(),
            "UiVersion": sys.version,
            "UI": Path(sys.executable).as_posix(),
            "SelectedItem": f.__name__,
            "Errors": [],
        }
        # run function and obtain errors if it failed
        try:
            d["Result"] = f(*args, **kwargs)
        except Exception:
            d["Errors"].append(traceback.format_exc())
            d["Result"] = None
        d["EndTime"] = datetime.now()

        # TODO - make this JSON dump into an in-memory location to save on file IO overhead.
        with open(output_file, "w+") as fp:
            dump(d, fp, cls=BHoMJSONEncoder)
        # print function here to enable downstream processes to access the location where the data is stored for loading into BHoM.
        print(output_file, file=sys.stdout)

        return f(*args, **kwargs)

    return wrapper
