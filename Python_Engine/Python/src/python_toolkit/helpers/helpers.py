import re
from datetime import timedelta
from typing import Any

import pandas as pd
from caseconverter import snakecase

from ..bhom.analytics import bhom_analytics

def sanitise_string(string: str) -> str:
    """Sanitise a string so that only path-safe characters remain."""

    keep_characters = r"[^.A-Za-z0-9_-]"

    return re.sub(keep_characters, "_", string).replace("__", "_").rstrip()

def convert_keys_to_snake_case(d: dict | list | Any):
    """Given a dictionary, convert all keys to snake_case."""
    keys_to_skip = ["_t"]
    if isinstance(d, dict):
        return {
            snakecase(k) if k not in keys_to_skip else k: convert_keys_to_snake_case(v)
            for k, v in d.items()
        }
    if isinstance(d, list):
        return [convert_keys_to_snake_case(x) for x in d]

    return d

@bhom_analytics()
def timedelta_tostring(time_delta: timedelta) -> str:
    """timedelta objects don't have a nice string representation, so this function converts them.

    Args:
        time_delta (datetime.timedelta):
            The timedelta object to convert.
    Returns:
        str:
            A string representation of the timedelta object.
    """
    s = time_delta.seconds
    hours, remainder = divmod(s, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}"

@bhom_analytics()
def decay_rate_smoother(
    series: pd.Series,
    difference_threshold: float = -10,
    transition_window: int = 4,
    ewm_span: float = 1.25,
) -> pd.Series:
    """Helper function that adds a decay rate to a time-series for values dropping significantly
        below the previous values.

    Args:
        series (pd.Series):
            The series to modify
        difference_threshold (float, optional):
            The difference between current/previous values which class as a "transition".
            Defaults to -10.
        transition_window (int, optional):
            The number of values after the "transition" within which an exponentially weighted mean
             should be applied. Defaults to 4.
        ewm_span (float, optional):
            The rate of decay. Defaults to 1.25.

    Returns:
        pd.Series:
            A modified series
    """

    # Find periods of major transition (where values vary significantly)
    transition_index = series.diff() < difference_threshold

    # Get boolean index for all periods within window from the transition indices
    ewm_mask = []
    n = 0
    for i in transition_index:
        if i:
            n = 0
        if n < transition_window:
            ewm_mask.append(True)
        else:
            ewm_mask.append(False)
        n += 1

    # Run an EWM to get the smoothed values following changes to values
    ewm_smoothed: pd.Series = series.ewm(span=ewm_span).mean()

    # Choose from ewm or original values based on ewm mask
    new_series = ewm_smoothed.where(ewm_mask, series)

    return new_series

@bhom_analytics()
def remove_leap_days(pd_object: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """A removal of all timesteps within a time-indexed pandas
    object where the day is the 29th of February."""

    if not isinstance(pd_object.index, pd.DatetimeIndex):
        raise ValueError("The object provided should be datetime-indexed.")

    mask = (pd_object.index.month == 2) & (pd_object.index.day == 29)

    return pd_object[~mask]

@bhom_analytics()
def safe_filename(filename: str) -> str:
    """Remove all non-alphanumeric characters from a filename."""
    return "".join(
        [c for c in filename if c.isalpha() or c.isdigit() or c == " "]
    ).strip()
