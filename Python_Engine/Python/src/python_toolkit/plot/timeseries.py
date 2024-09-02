"""Methods for plotting time-indexed data."""

from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

from ..bhom.analytics import bhom_analytics
from ..helpers import validate_timeseries


@bhom_analytics()
def timeseries(
    series: pd.Series,
    ax: plt.Axes = None,
    xlims: tuple[datetime] = None,
    ylims: tuple[datetime] = None,
    **kwargs,
) -> plt.Axes:
    """Create a timeseries plot of a pandas Series.

    Args:
        series (pd.Series):
            The pandas Series to plot. Must have a datetime index.
        ax (plt.Axes, optional):
            An optional plt.Axes object to populate. Defaults to None, which creates a new plt.Axes object.
        xlims (tuple[datetime], optional):
            Set the x-limits. Defaults to None.
        ylims (tuple[datetime], optional):
            Set the y-limits. Defaults to None.
        **kwargs:
            Additional keyword arguments to pass to the plt.plot() function.

    Returns:
        plt.Axes:
            The populated plt.Axes object.
    """

    validate_timeseries(series)

    if ax is None:
        ax = plt.gca()

    ax.plot(series.index, series.values, **kwargs)  ## example plot here

    # TODO - add cmap arg to color line by y value -
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html

    if xlims is None:
        ax.set_xlim(series.index.min(), series.index.max())
    else:
        ax.set_xlim(xlims)
    if ylims is None:
        ax.set_ylim(ax.get_ylim())
    else:
        ax.set_ylim(ylims)

    return ax