from __future__ import annotations
from json import JSONEncoder, dump
import sys
from datetime import datetime, date
from pathlib import Path
import numpy as np
import inspect
import pandas as pd
from uuid import uuid4
import socket
import traceback
from tempfile import gettempdir


class CustomEncoder(JSONEncoder):
    """A custom JSONEncoder class capable of serialising non-native Python datatypes into a JSON file-like object."""

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


class ToBHoM(object):
    """Decorator method to serialise data output from Python method into a BHoM readable JSON format."""

    def __init__(self):
        self.filename = Path(f"C:/Temp/bhom_python_{uuid4()}.json")
        self.method_input = input

    def __call__(self, func):
        """Serialise the output of the function to a JSON file

        Args:
            func (method): A Python function that returns an object that is JSON serialisable.
        """

        def wrapper(*args, **kwargs):

            errors = []
            start_time: datetime = datetime.now()
            try:
                result = func(*args, **kwargs)
            except Exception:
                errors.append(traceback.format_exc())
                result = None
            end_time: datetime = datetime.now()

            d = {
                "Computer": socket.gethostname(),
                "Data": result,
                "EndTime": end_time,
                "Errors": [str(i) for i in errors],
                "FileName": Path(inspect.getfile(func)).as_posix(),
                "SelectedItem": func.__name__,
                "StartTime": start_time,
                "UI": Path(sys.executable).as_posix(),
                "UiVersion": sys.version,
            }
            # TODO - make this JSON dump into an in-memory location to save on file IO overhead.
            with open(self.filename, "w+") as fp:
                dump(d, fp, cls=CustomEncoder)

            # print function here to enable downstream processes to access the location where the data is stored for loading into BHoM.
            print(self.filename, file=sys.stdout)

            return result

        return wrapper
