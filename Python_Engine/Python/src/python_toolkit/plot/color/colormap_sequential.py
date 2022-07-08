from typing import Tuple, Union

import numpy as np
from matplotlib.colors import (
    LinearSegmentedColormap,
    is_color_like,
    rgb2hex,
)


def colormap_sequential(
    *colors: Union[str, float, int, Tuple]
) -> LinearSegmentedColormap:
    """
    Create a sequential colormap from a list of input colors.

    Args:
        colors (Union[str, float, int, Tuple]): A list of colors according to their hex-code, string name, character code or RGBA values.

    Returns:
        LinearSegmentedColormap: A matplotlib colormap.

    Examples:
    >> colormap_sequential("green", "#F034A3", (0.5, 0.2, 0.8), "y")
    """
    for color in colors:
        if not isinstance(color, (str, float, int, tuple)):
            raise KeyError(f"{color} not recognised as a valid color string.")

    if len(colors) < 2:
        raise KeyError("Not enough colors input to create a colormap.")

    fixed_colors = []
    for c in colors:
        if is_color_like(c):
            try:
                fixed_colors.append(rgb2hex(c))
            except:
                fixed_colors.append(c)
        else:
            raise KeyError(f"{c} not recognised as a valid color string.")
    return LinearSegmentedColormap.from_list(
        f"{'_'.join(fixed_colors)}",
        list(zip(np.linspace(0, 1, len(fixed_colors)), fixed_colors)),
        N=256,
    )
