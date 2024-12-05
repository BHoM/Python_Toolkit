"""Root for Python_Toolkit tests."""

from pathlib import Path

import pandas as pd

# identifier for all downstream processes
BASE_IDENTIFIER = "PythonBHoM_pytest"

ASSET_DIR = Path(__file__).parent / "assets"


def get_timeseries():
    """Helper method to load example timeseries data."""
    df = pd.read_csv(ASSET_DIR / "example_timeseries.csv", index_col="Timestamp")
    df = df.set_index(pd.to_datetime(df.index))
    return pd.Series(df["Value"], index=df.index)


TIMESERIES_COLLECTION = get_timeseries()
EXAMPLE_IMAGE = ASSET_DIR / "example_pixelextraction.png"
