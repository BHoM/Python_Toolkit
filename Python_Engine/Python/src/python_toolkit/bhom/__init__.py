from __future__ import annotations

import functools
import inspect
import socket
import sys
import traceback
from datetime import date, datetime
from json import JSONEncoder, dump
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd


class BHoMJSONEncoder(JSONEncoder):
    """A custom BHoM JSONEncoder class capable of serialising non-native Python datatypes into a JSONable object."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return obj.as_posix()
        return JSONEncoder.default(self, obj)


def bhom_analytics(f):
    """A wrapper function used to capture usage analytics of the wrapped function"""

    @functools.wraps(f)
    def wrapper(*args, **kwds):
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

        return f(*args, **kwds)

    return wrapper
