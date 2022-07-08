from typing import List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import BoundaryNorm, Colormap
from matplotlib.figure import Figure


# TODO - Enable auto-rescaling of X-axis (date) based on length of data being visualised
def timeseries_heatmap(
    series: pd.Series,
    cmap: Colormap = "viridis",
    norm: BoundaryNorm = None,
    vlims: List[float] = None,
    title: str = None,
) -> Figure:
    """Plot a heatmap for a Pandas Series object.

    Args:
        series (pd.Series): A time-indexed Pandas Series object.
        cmap (Colormap, optional): The colormap to use in this heatmap. Defaults to "viridis".
        norm (BoundaryNorm, optional): A matplotlib BoundaryNorm object describing value thresholds. Defaults to None.
        vlims (List[float], optional): The limits to which values should be plotted (useful for comparing between different cases). Defaults to None.
        title (str, optional): A title to place at the top of the plot. Defaults to None.

    Returns:
        Figure: A matplotlib Figure object.
    """

    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError(f"Series passed is not datetime indexed.")

    if norm and vlims:
        raise ValueError("You cannot pass both vlims and a norm value to this method.")

    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    fig, ax = plt.subplots(1, 1, figsize=(15, 5))

    # Reshape data into time/day matrix
    day_time_matrix = (
        series.to_frame()
        .pivot_table(columns=series.index.date, index=series.index.time)
        .values[::-1]
    )

    # Plot data
    heatmap = ax.imshow(
        day_time_matrix,
        extent=[
            mdates.date2num(series.index.min()),
            mdates.date2num(series.index.max()),
            726449,
            726450,
        ],
        aspect="auto",
        cmap=cmap,
        norm=norm,
        interpolation="none",
        vmin=None if vlims is None else vlims[0],
        vmax=None if vlims is None else vlims[1],
    )

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.yaxis_date()
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax.tick_params(labelleft=True, labelright=True, labelbottom=True)
    plt.setp(ax.get_xticklabels(), ha="left", color="k")
    plt.setp(ax.get_yticklabels(), color="k")

    [
        ax.spines[spine].set_visible(False)
        for spine in ["top", "bottom", "left", "right"]
    ]

    ax.grid(b=True, which="major", color="white", linestyle=":", alpha=1)

    cb = fig.colorbar(
        heatmap,
        orientation="horizontal",
        drawedges=False,
        fraction=0.05,
        aspect=100,
        pad=0.075,
    )
    plt.setp(plt.getp(cb.ax.axes, "xticklabels"), color="k")
    cb.outline.set_visible(False)

    if title is None:
        ax.set_title(series.name, color="k", y=1, ha="left", va="bottom", x=0)
    else:
        ax.set_title(
            f"{series.name} - {title}",
            color="k",
            y=1,
            ha="left",
            va="bottom",
            x=0,
        )

    # Tidy plot
    plt.tight_layout()

    return fig
