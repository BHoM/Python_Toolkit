"""Methods for plotting heatmaps from time-indexed data."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..bhom.analytics import bhom_analytics
from ..helpers.timeseries import validate_timeseries


@bhom_analytics()
def heatmap(
    series: pd.Series,
    ax: plt.Axes = None,
    **kwargs,
) -> plt.Axes:
    """Create a heatmap of a pandas Series.

    Args:
        series (pd.Series):
            The pandas Series to plot. Must have a datetime index.
        ax (plt.Axes, optional):
            An optional plt.Axes object to populate. Defaults to None, which creates a new plt.Axes object.
        **kwargs:
            Additional keyword arguments to pass to plt.pcolormesh().
            show_colorbar (bool, optional):
                If True, show the colorbar. Defaults to True.
            title (str, optional):
                The title of the plot. Defaults to None.
            mask (List[bool], optional):
                A list of booleans to mask the data. Defaults to None.

    Returns:
        plt.Axes:
            The populated plt.Axes object.
    """

    validate_timeseries(series)

    if ax is None:
        ax = plt.gca()

    day_time_matrix = (
        series.dropna()
        .to_frame()
        .pivot_table(columns=series.index.date, index=series.index.time)
    )
    x = mdates.date2num(day_time_matrix.columns.get_level_values(1))
    y = mdates.date2num(
        pd.to_datetime([f"2017-01-01 {i}" for i in day_time_matrix.index])
    )
    z = day_time_matrix.values

    if "mask" in kwargs:
        if len(kwargs["mask"]) != len(series):
            raise ValueError(
                f"Length of mask ({len(kwargs['mask'])}) must match length of data ({len(series)})."
            )
        z = np.ma.masked_array(z, mask=kwargs.pop("mask"))

    # handle non-standard kwargs
    extend = kwargs.pop("extend", "neither")
    title = kwargs.pop("title", series.name)
    show_colorbar = kwargs.pop("show_colorbar", True)

    # Plot data
    pcm = ax.pcolormesh(
        x,
        y,
        z[:-1, :-1],
        **kwargs,
    )

    ax.xaxis_date()
    if len(set(series.index.year)) > 1:
        date_formatter = mdates.DateFormatter("%b %Y")
    else:
        date_formatter = mdates.DateFormatter("%b")
    ax.xaxis.set_major_formatter(date_formatter)

    ax.yaxis_date()
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax.tick_params(labelleft=True, labelbottom=True)
    plt.setp(ax.get_xticklabels(), ha="left")

    for spine in ["top", "bottom", "left", "right"]:
        ax.spines[spine].set_visible(False)

    for i in ax.get_xticks():
        ax.axvline(i, color="w", ls=":", lw=0.5, alpha=0.5)
    for i in ax.get_yticks():
        ax.axhline(i, color="w", ls=":", lw=0.5, alpha=0.5)

    if show_colorbar:
        cb = plt.colorbar(
            pcm,
            ax=ax,
            orientation="horizontal",
            drawedges=False,
            fraction=0.05,
            aspect=100,
            pad=0.075,
            extend=extend,
            label=series.name,
        )
        cb.outline.set_visible(False)

    ax.set_title(title)

    return ax