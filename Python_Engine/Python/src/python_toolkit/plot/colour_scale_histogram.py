"""Histogram of data drawn over the bands of a colour scale."""

import numpy as np
from matplotlib.figure import Figure

from python_toolkit.colour_scales import ColourScale


def colour_scale_histogram(scale: ColourScale, values: np.ndarray, figsize: tuple[float, float] = (5.6, 1.3),
                           background: str = "#ffffff", foreground: str = "#000000") -> Figure:
    """Plot a histogram of the data over the scale's colours, with a line at each threshold.

    Args:
        scale: The colour scale to show.
        values: Finite values the scale colours; with none, only the colours and thresholds are drawn.
        figsize: Figure size in inches.
        background: Figure background colour.
        foreground: Colour of the bars, threshold lines and axis.

    Returns:
        Figure: The plot.
    """
    fig = Figure(figsize=figsize, dpi=100, facecolor=background)
    ax = fig.add_axes([0.0, 0.2, 1.0, 0.76], facecolor=background)
    cmap, norm = scale.cmap_and_norm()
    low, high = scale.value_range(values)
    xs = np.linspace(low, high, 400)
    ax.imshow(cmap(norm(xs))[np.newaxis, :, :], aspect="auto", extent=(low, high, 0, 1), alpha=0.85,
              origin="lower", zorder=0)
    if values.size:
        counts, edges = np.histogram(values, bins=30, range=(low, high))
        ax.bar(edges[:-1], counts / max(counts.max(), 1), width=np.diff(edges), align="edge", color=foreground,
               alpha=0.45, edgecolor=background, linewidth=0.6, zorder=1)
    for threshold in scale.thresholds:
        if low <= threshold <= high:
            ax.axvline(threshold, color=foreground, linewidth=1.2, zorder=2)
    ax.set_xlim(low, high)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([])
    ax.tick_params(labelsize=7, colors=foreground)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(foreground)
    return fig
