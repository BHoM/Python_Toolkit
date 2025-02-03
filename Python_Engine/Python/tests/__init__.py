from pathlib import Path
import pandas as pd
import matplotlib as mpl


# identifier for all downstream processes
BASE_IDENTIFIER = "PythonBHoM_pytest"

def get_timeseries():
    df = pd.read_csv(Path(__file__).parent / "assets" / "example_timeseries.csv", index_col="Timestamp")
    df = df.set_index(pd.to_datetime(df.index))
    return pd.Series(df["Value"], index=df.index)

TIMESERIES_COLLECTION = get_timeseries()

#use 'agg' for testing plot methods, as tkinter occasionally throws strange errors (missing component/library when component isn't missing) when the default backend is used only when using pytest
mpl.use("agg")