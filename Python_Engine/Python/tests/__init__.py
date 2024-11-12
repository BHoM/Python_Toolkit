from pathlib import Path
import pandas as pd

# identifier for all downstream processes
BASE_IDENTIFIER = "PythonBHoM_pytest"

def get_timeseries():
    df = pd.read_csv(Path(__file__).parent / "assets" / "example_timeseries.csv", index_col="Timestamp")
    df = df.set_index(pd.to_datetime(df.index))
    return pd.Series(df["Value"], index=df.index)

TIMESERIES_COLLECTION = get_timeseries()