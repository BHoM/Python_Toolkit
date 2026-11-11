"""Reading numeric values out of whatever data a colour scale is given."""

import math
from typing import Any, Iterable, Optional

import numpy as np


def finite_values(data: Optional[Iterable]) -> np.ndarray:
    """Read the finite numbers from any iterable, flattened.

    Args:
        data: Values of any shape or type, or None.

    Returns:
        np.ndarray: The finite values as floats; None, NaN, infinities and non-numbers are dropped.
    """
    if data is None:
        return np.empty(0)
    try:  # fast path: already numeric (or numeric strings)
        numbers = np.ravel(np.asarray(data if hasattr(data, "__len__") else list(data), dtype=float))
    except (TypeError, ValueError):  # mixed input: keep the numbers, drop the rest
        numbers = np.array([_to_float(v) for v in np.ravel(np.asarray(list(data), dtype=object))], dtype=float)
    return numbers[np.isfinite(numbers)]


def _to_float(value: Any) -> float:
    """Convert a value to a float, or NaN if it is not a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan
