import re
from enum import Enum, auto

import numpy as np
import pandas as pd

from ..bhom.analytics import bhom_analytics

class DecayMethod(Enum):
    """An enumeration of decay methods."""

    LINEAR = auto()
    PARABOLIC = auto()
    SIGMOID = auto()

@bhom_analytics()
def proximity_decay(
    value: float,
    distance_to_value: float,
    max_distance: float,
    decay_method: DecayMethod = DecayMethod.LINEAR,
) -> float:
    """Calculate the "decayed" value based on proximity (up to a maximum distance).

    Args:
        value (float):
            The value to be distributed.
        distance_to_value (float):
            A distance at which to return the magnitude.
        max_distance (float):
            The maximum distance to which magnitude is to be distributed. Beyond this, the input
            value is 0.
        decay_method (DecayMethod, optional):
            A type of distribution (the shape of the distribution profile). Defaults to "DecayMethod.LINEAR".

    Returns:
        float:
            The value at the given distance.
    """

    distance_to_value = np.interp(distance_to_value, [0, max_distance], [0, 1])

    if decay_method == DecayMethod.LINEAR:
        return (1 - distance_to_value) * value
    if decay_method == DecayMethod.PARABOLIC:
        return (-(distance_to_value**2) + 1) * value
    if decay_method == DecayMethod.SIGMOID:
        return (1 - (0.5 * (np.sin(distance_to_value * np.pi - np.pi / 2) + 1))) * value

    raise ValueError(f"Unknown curve type: {decay_method}")

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
