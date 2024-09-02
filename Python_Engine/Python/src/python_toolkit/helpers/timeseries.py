from typing import Any
import pandas as pd

from ..bhom.analytics import bhom_analytics

@bhom_analytics()
def validate_timeseries(
    obj: Any,
    is_annual: bool = False,
    is_hourly: bool = False,
    is_contiguous: bool = False,
) -> None:
    """Check if the input object is a pandas Series, and has a datetime index.

    Args:
        obj (Any):
            The object to check.
        is_annual (bool, optional):
            If True, check that the series is annual. Defaults to False.
        is_hourly (bool, optional):
            If True, check that the series is hourly. Defaults to False.
        is_contiguous (bool, optional):
            If True, check that the series is contiguous. Defaults to False.

    Raises:
        TypeError: If the object is not a pandas Series.
        TypeError: If the series does not have a datetime index.
        ValueError: If the series is not annual.
        ValueError: If the series is not hourly.
        ValueError: If the series is not contiguous.
    """
    if not isinstance(obj, pd.Series):
        raise TypeError("series must be a pandas Series")
    if not isinstance(obj.index, pd.DatetimeIndex):
        raise TypeError("series must have a datetime index")
    if is_annual:
        if (obj.index.day_of_year.nunique() != 365) or (
            obj.index.day_of_year.nunique() != 366
        ):
            raise ValueError("series is not annual")
    if is_hourly:
        if obj.index.hour.nunique() != 24:
            raise ValueError("series is not hourly")
    if is_contiguous:
        if not obj.index.is_monotonic_increasing:
            raise ValueError("series is not contiguous")


@bhom_analytics()
def timeseries_summary_monthly(series: pd.Series, bins: list[float], bin_names: list[str] = None, density: bool = False):
    if not isinstance(series, pd.Series):
        raise ValueError("The series must be a pandas series.")

    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("The series must have a time series.")

    df = pd.cut(series, bins=bins, labels=bin_names, include_lowest=True)

    if df.isna().any():
        raise ValueError(
            f"The input value/s are outside the range of the given bins ({bins[0]} <= x <= {bins[-1]})."
        )
    
    counts = df.groupby(series.index.month).value_counts().unstack().sort_index(axis=0)
    counts.columns.name = None
    counts.index.name = "Month"
    if density:
        return counts.div(counts.sum(axis=1), axis=0)
    return counts