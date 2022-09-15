from datetime import date, datetime
from json import JSONEncoder
from pathlib import Path

import numpy as np
import pandas as pd


class Encoder(JSONEncoder):
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
