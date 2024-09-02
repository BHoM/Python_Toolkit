"""Text and colour utility methods for plotting"""

from typing import Any
import numpy as np
from matplotlib.colors import colorConverter


def create_title(text: str, plot_type: str) -> str:
    """Create a title for a plot.

    Args:
        text (str):
            The title of the plot.
        plot_type (str):
            The type of plot.

    Returns:
        str:
            The title of the plot.
    """
    return "\n".join(
        [
            i
            for i in [
                text,
                plot_type,
            ]
            if i is not None
        ]
    )


def contrasting_colour(color: Any):
    """Calculate the contrasting color for a given color.

    Args:
        color (Any):
            matplotlib color or sequence of matplotlib colors - Hex code,
            rgb-tuple, or html color name.

    Returns:
        str:
            String code of the contrasting color.
    """
    return ".15" if relative_luminance(color) > 0.408 else "w"


def relative_luminance(color: Any):
    """Calculate the relative luminance of a color according to W3C standards

    Args:
        color (Any):
            matplotlib color or sequence of matplotlib colors - Hex code,
            rgb-tuple, or html color name.

    Returns:
        float:
            Luminance value between 0 and 1.
    """
    rgb = colorConverter.to_rgba_array(color)[:, :3]
    rgb = np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lum = rgb.dot([0.2126, 0.7152, 0.0722])
    try:
        return lum.item()
    except ValueError:
        return lum