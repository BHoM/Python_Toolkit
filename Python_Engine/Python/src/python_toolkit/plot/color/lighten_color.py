import colorsys
from typing import Tuple, Union

from matplotlib.colors import (
    cnames,
    to_rgb,
)


def lighten_color(color: Union[str, Tuple], amount: float = 0.5) -> Tuple[float]:
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.

    Args:
        color (str): A clolor-like string.
        amount (float): The amount of lightening to apply.

    Returns:
        Tuple[float]: An RGB value.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    try:
        c = cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
