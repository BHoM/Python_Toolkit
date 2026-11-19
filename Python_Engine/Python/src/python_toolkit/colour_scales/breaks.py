"""Suggesting colour scale thresholds from the data the scale will colour."""

import math
from enum import Enum
from typing import Callable, Iterable, Union

import numpy as np

from python_toolkit.colour_scales.errors import ColourScaleError
from python_toolkit.colour_scales.jenks import jenks_breaks
from python_toolkit.colour_scales.values import finite_values


class BreakMethod(str, Enum):
    """Ways of splitting data into bands.

    EQUAL: equal-width bands across the data range.
    QUANTILE: roughly the same number of values in each band.
    JENKS: natural breaks; the bands that minimise the spread of values within each band.
    NICE: equal-width bands on rounded 1 / 2 / 5 x 10^n steps.
    LOG: bands of equal ratio, rounded to 3 significant figures; needs every value above zero.
    """

    EQUAL = "equal"
    QUANTILE = "quantile"
    JENKS = "jenks"
    NICE = "nice"
    LOG = "log"


def suggest_thresholds(data: Iterable, bands: int, method: Union[BreakMethod, str] = BreakMethod.NICE) -> list[float]:
    """Suggest the thresholds that split data into bands.

    Args:
        data: Values the scale will colour; non-numeric and non-finite values are ignored.
        bands: Number of bands wanted, at least 2.
        method: How to place the breaks (see BreakMethod).

    Returns:
        list[float]: `bands - 1` strictly increasing thresholds.

    Raises:
        ColourScaleError: If the arguments are invalid, or the data cannot be split that way.
    """
    if bands < 2:
        raise ColourScaleError("A threshold scale needs at least 2 bands.")
    try:
        method = BreakMethod(method)
    except ValueError:
        options = tuple(m.value for m in BreakMethod)
        raise ColourScaleError(f"Method must be one of {options}, not '{method}'.") from None
    values = finite_values(data)
    if values.size == 0:
        raise ColourScaleError("No numeric values to suggest thresholds from.")
    low, high = float(values.min()), float(values.max())
    if low == high:
        return [low + i for i in range(1, bands)]
    return _BREAK_FUNCTIONS[method](values, bands)


def _equal_breaks(values: np.ndarray, bands: int) -> list[float]:
    """Breaks at equal steps across the data range."""
    return [float(v) for v in np.linspace(values.min(), values.max(), bands + 1)[1:-1]]


def _quantile_breaks(values: np.ndarray, bands: int) -> list[float]:
    """Breaks that put roughly the same number of values in each band."""
    cuts = sorted({float(c) for c in np.quantile(values, np.linspace(0, 1, bands + 1)[1:-1])})
    if len(cuts) < bands - 1:
        raise ColourScaleError("Too many repeated values for that many quantile bands; use fewer bands.")
    return cuts


def _log_breaks(values: np.ndarray, bands: int) -> list[float]:
    """Breaks at equal ratios across the data range, rounded to 3 significant figures."""
    low, high = float(values.min()), float(values.max())
    if low <= 0:
        raise ColourScaleError("Logarithmic breaks need every value above zero; use another break method.")
    cuts = [float(f"{v:.3g}") for v in np.geomspace(low, high, bands + 1)[1:-1]]
    if any(upper <= lower for lower, upper in zip(cuts, cuts[1:])) or cuts[0] <= low or cuts[-1] >= high:
        raise ColourScaleError("The data range is too narrow for that many logarithmic bands; use fewer bands.")
    return cuts


def _nice_breaks(values: np.ndarray, bands: int) -> list[float]:
    """Rounded breaks (multiples of 1, 2, 2.5 or 5 x 10^n) strictly inside the data range.

    Picks the step with the fewest breaks that is still enough, then keeps the number wanted, spread
    evenly from the first to the last, so every band contains data and the end bands stay small.
    Where the step does not divide evenly, some bands are two steps wide.
    """
    low, high = float(values.min()), float(values.max())
    wanted = bands - 1
    candidates = _rounded_break_candidates(low, high, wanted)
    if not candidates:  # range too narrow for rounded breaks
        return [float(v) for v in np.linspace(low, high, wanted + 2)[1:-1]]
    return [candidates[i] for i in np.linspace(0, len(candidates) - 1, wanted).round().astype(int)]


def _rounded_break_candidates(low: float, high: float, wanted: int) -> list[float]:
    """Every multiple of the best rounded step strictly between low and high, or [] if no step gives enough."""
    exponent = math.floor(math.log10((high - low) / (wanted + 1)))
    best_score, best_breaks = math.inf, []
    for power in (exponent - 1, exponent, exponent + 1):
        for factor in (1, 2, 2.5, 5):
            step = factor * 10 ** power
            breaks = [round(k * step, 10) for k in range(math.floor(low / step) + 1, math.ceil(high / step))]
            if len(breaks) < wanted:
                continue
            score = len(breaks) - wanted + (0.5 if factor == 2.5 else 0.0)  # prefer rounder steps
            if score < best_score:
                best_score, best_breaks = score, breaks
    return best_breaks


_BREAK_FUNCTIONS: dict[BreakMethod, Callable[[np.ndarray, int], list[float]]] = {
    BreakMethod.EQUAL: _equal_breaks,
    BreakMethod.QUANTILE: _quantile_breaks,
    BreakMethod.JENKS: jenks_breaks,
    BreakMethod.NICE: _nice_breaks,
    BreakMethod.LOG: _log_breaks,
}
