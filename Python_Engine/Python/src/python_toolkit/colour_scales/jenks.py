"""Fisher-Jenks natural breaks."""

import numpy as np

from python_toolkit.colour_scales.errors import ColourScaleError

MAX_VALUES = 2000  # larger data is thinned, evenly through its sorted values, before the search


def jenks_breaks(values: np.ndarray, bands: int) -> list[float]:
    """Split values into the bands with the least total squared deviation from each band's mean.

    Args:
        values: Finite values to split.
        bands: Number of bands wanted.

    Returns:
        list[float]: `bands - 1` breaks; each is the lowest value of the band above it.

    Raises:
        ColourScaleError: If there are fewer distinct values than bands.
    """
    ordered = np.sort(values)
    if ordered.size > MAX_VALUES:
        ordered = ordered[np.linspace(0, ordered.size - 1, MAX_VALUES).round().astype(int)]
    x, counts = np.unique(ordered, return_counts=True)
    if x.size < bands:
        raise ColourScaleError("Too few distinct values for that many natural-break bands; use fewer bands.")
    band_starts = _best_band_starts(x, counts.astype(float), bands)
    return _read_breaks(x, band_starts, bands)


def _best_band_starts(x: np.ndarray, weights: np.ndarray, bands: int) -> np.ndarray:
    """Dynamic programme over the distinct values `x` (each weighted by how often it occurs).

    Returns:
        np.ndarray: `starts[k, j]` is where the last band begins in the best split of x[:j + 1] into k + 1 bands.
    """
    n = x.size
    cum_w, cum_wx, cum_wx2 = (np.concatenate([[0.0], np.cumsum(a)]) for a in (weights, weights * x, weights * x * x))

    def squared_deviation(starts: np.ndarray, end: int) -> np.ndarray:
        """Squared deviation of x[start:end + 1] about its mean, for each start."""
        w = cum_w[end + 1] - cum_w[starts]
        wx = cum_wx[end + 1] - cum_wx[starts]
        wx2 = cum_wx2[end + 1] - cum_wx2[starts]
        return wx2 - wx * wx / w

    best_cost = np.full((bands, n), np.inf)
    band_starts = np.zeros((bands, n), dtype=int)
    best_cost[0] = [squared_deviation(np.array([0]), j)[0] for j in range(n)]
    for k in range(1, bands):
        for j in range(k, n):
            starts = np.arange(k, j + 1)
            total = best_cost[k - 1, starts - 1] + squared_deviation(starts, j)
            pick = int(np.argmin(total))
            best_cost[k, j], band_starts[k, j] = total[pick], starts[pick]
    return band_starts


def _read_breaks(x: np.ndarray, band_starts: np.ndarray, bands: int) -> list[float]:
    """Walk back through the band starts from the last value to read off each break."""
    breaks, end = [], x.size - 1
    for k in range(bands - 1, 0, -1):
        start = int(band_starts[k, end])
        breaks.append(float(x[start]))
        end = start - 1
    return breaks[::-1]
