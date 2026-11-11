"""Colour palettes: matplotlib's colour maps plus the toolkit's own.

Importing this package registers the toolkit palettes with matplotlib, so their names work
anywhere a colour map name is accepted:

    palette_names("colourblind")       # ['viridis', 'cividis', ..., 'okabe_ito']
    sample_colours("okabe_ito", 4)     # four hex colours
"""

from python_toolkit.palettes.palette import Palette
from python_toolkit.palettes.registry import (
    PaletteGroup,
    is_categorical,
    palette_names,
    register_toolkit_palettes,
    sample_colours,
)
from python_toolkit.palettes.toolkit_palettes import TOOLKIT_PALETTES

register_toolkit_palettes()

__all__ = [
    "Palette",
    "PaletteGroup",
    "TOOLKIT_PALETTES",
    "is_categorical",
    "palette_names",
    "register_toolkit_palettes",
    "sample_colours",
]
