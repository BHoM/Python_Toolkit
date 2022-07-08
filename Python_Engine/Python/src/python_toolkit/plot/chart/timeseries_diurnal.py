from typing import Tuple, Union

import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.figure import Figure


def timeseries_diurnal(
    series: pd.Series,
    color: Union[str, Tuple] = "k",
    ylabel: str = None,
    title: str = None,
) -> Figure:
    """Plot a heatmap for a Pandas Series object.

    Args:
        series (pd.Series): A time-indexed Pandas Series object.
        color (Union[str, Tuple], optional): The color to use for this diurnal plot.
        ylabel (str, optional): A label to be placed on the y-axis.
        title (str, optional): A title to place at the top of the plot. Defaults to None.

    Returns:
        Figure: A matplotlib Figure object.
    """

    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError(f"Series passed is not datetime indexed.")

    target_index = pd.MultiIndex.from_arrays(
        [
            [x for xs in [[i + 1] * 24 for i in range(12)] for x in xs],
            [x for xs in [range(0, 24, 1) for i in range(12)] for x in xs],
        ],
        names=["month", "hour"],
    )

    # groupby and obtain min, quant, mean, quant, max values
    grp = series.groupby([series.index.month, series.index.hour], axis=0)
    _min = grp.min().reindex(target_index)
    _lower = grp.quantile(0.05).reindex(target_index)
    _mean = grp.mean().reindex(target_index)
    _upper = grp.quantile(0.95).reindex(target_index)
    _max = grp.max().reindex(target_index)

    fig, ax = plt.subplots(1, 1, figsize=(15, 4))

    x_values = range(288)
    idx = [
        x
        for xs in [
            pd.date_range(f"2021-{i+1:02d}-01 00:00:00", periods=24, freq="60T")
            for i in range(12)
        ]
        for x in xs
    ]

    # for each month, plot the diurnal profile
    for i in range(0, 288)[::24]:
        ax.plot(
            x_values[i : i + 24],
            _mean[i : i + 24],
            color=color,
            lw=2,
            label="Average",
            zorder=7,
        )
        ax.plot(
            x_values[i : i + 24],
            _lower[i : i + 24],
            color=color,
            lw=1,
            label="Average",
            ls=":",
        )
        ax.plot(
            x_values[i : i + 24],
            _upper[i : i + 24],
            color=color,
            lw=1,
            label="Average",
            ls=":",
        )
        ax.fill_between(
            x_values[i : i + 24],
            _min[i : i + 24],
            _max[i : i + 24],
            color=color,
            alpha=0.2,
            label="Range",
        )
        ax.fill_between(
            x_values[i : i + 24],
            _lower[i : i + 24],
            _upper[i : i + 24],
            color="white",
            alpha=0.5,
            label="Range",
        )
        ax.set_ylabel(
            series.name,
            labelpad=2,
        )

    ax.xaxis.set_major_locator(mticker.FixedLocator(range(0, 288, 24)))
    ax.xaxis.set_minor_locator(mticker.FixedLocator(range(12, 288, 24)))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(7))
    [ax.spines[spine].set_visible(False) for spine in ["top", "right"]]
    [ax.spines[j].set_color("k") for j in ["bottom", "left"]]
    ax.set_xlim([0, 287])
    ax.set_xticklabels(
        [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ],
        minor=False,
        ha="left",
        color="k",
    )
    ax.grid(visible=True, which="major", axis="both", c="k", ls="--", lw=1, alpha=0.2)
    ax.grid(visible=True, which="minor", axis="both", c="k", ls=":", lw=1, alpha=0.1)

    handles = [
        mlines.Line2D([0], [0], label="Average", color="k", lw=2),
        mlines.Line2D([0], [0], label="5-95%ile", color="k", lw=1, ls=":"),
        mpatches.Patch(color="grey", label="Range", alpha=0.3),
    ]

    lgd = ax.legend(
        handles=handles,
        bbox_to_anchor=(0.5, -0.2),
        loc=8,
        ncol=6,
        borderaxespad=0,
        frameon=False,
    )
    lgd.get_frame().set_facecolor((1, 1, 1, 0))
    [plt.setp(text, color="k") for text in lgd.get_texts()]

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if title is None:
        ax.set_title(
            f"Monthly average diurnal profile\n{series.name}",
            color="k",
            y=1,
            ha="left",
            va="bottom",
            x=0,
        )
    else:
        ax.set_title(f"{title}", color="k", y=1, ha="left", va="bottom", x=0)

    plt.tight_layout()

    return fig
