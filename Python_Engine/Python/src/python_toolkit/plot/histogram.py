"""Methods for plotting binned data"""

import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from ..bhom.analytics import bhom_analytics
from ..helpers.timeseries import validate_timeseries, timeseries_summary_monthly
from .utilities import contrasting_colour

@bhom_analytics()
def histogram(
    series: pd.Series,
    ax: plt.Axes = None,
    bins: list[float] | list[int] = None,
    **kwargs,
    ) -> plt.Axes:
    if bins is None:
        bins = np.linspace(series.values.min(), series.values.max(), 31)
    elif len(bins) <= 1:
        bins = np.linspace(series.values.min(), series.values.max(), 31)

    if ax is None:
        ax = plt.gca()

    ax.hist(series.values, bins=bins, label = series.name, density=False)

    show_legend = kwargs.pop("show_legend", True)

    if show_legend:
        ax.legend()

    return ax

@bhom_analytics()
def monthly_proportional_histogram(
    series: pd.Series,
    bins: list[float],
    ax: plt.Axes = None,
    labels: list[str] = None,
    show_year_in_label: bool = False,
    show_labels: bool = False,
    show_legend: bool = False,
    **kwargs,
) -> plt.Axes:
    """Create a monthly histogram of a pandas Series.

    Args:
        series (pd.Series):
            The pandas Series to plot. Must have a datetime index.
        bins (list[float]):
            The bins to use for the histogram.
        ax (plt.Axes, optional):
            An optional plt.Axes object to populate. Defaults to None, which creates a new plt.Axes object.
        labels (list[str], optional):
            The labels to use for the histogram. Defaults to None, which uses the bin edges.
        show_year_in_label (bool, optional):
            Whether to show the year in the x-axis label. Defaults to False.
        show_labels (bool, optional):
            Whether to show the labels on the bars. Defaults to False.
        show_legend (bool, optional):
            Whether to show the legend. Defaults to False.
        **kwargs:
            Additional keyword arguments to pass to plt.bar.

    Returns:
        plt.Axes:
            The populated plt.Axes object.
    """

    validate_timeseries(series)

    if ax is None:
        ax = plt.gca()
    
    counts = timeseries_summary_monthly(series, bins, labels, density=True)

    if show_year_in_label:
        counts.columns = [
            f"{year}\n{calendar.month_abbr[month]}" for year, month in counts.columns.values
        ]

    counts.plot(
        ax = ax,
        kind = "bar",
        stacked = True,
        width = kwargs.pop("width", 1),
        legend = False,
        **kwargs
        )

    ax.set_xlim(-0.5, len(counts) - 0.5)
    ax.set_ylim(0, 1)

    ax.set_xticklabels(
        [calendar.month_abbr[int(i._text)] for i in ax.get_xticklabels()],
        ha="center",
        rotation=0,
    )
    
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1))

    if show_legend:
        ax.legend(
            bbox_to_anchor=(1, 1),
            loc="upper left",
            borderaxespad=0.0,
            frameon=False,
        )

    if show_labels:
        for i, c in enumerate(ax.containers):
            label_colors = [contrasting_colour(i.get_facecolor()) for i in c.patches]
            labels = [
                f"{v.get_height():0.1%}" if v.get_height() > 0.15 else "" for v in c
            ]
            ax.bar_label(
                c,
                labels=labels,
                label_type="center",
                color=label_colors[i],
                fontsize="x-small",
            )

    return ax