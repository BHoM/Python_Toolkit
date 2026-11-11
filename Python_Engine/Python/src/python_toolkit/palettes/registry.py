"""Registering the toolkit palettes with matplotlib, and listing and sampling palettes by group."""

from enum import Enum
from typing import Optional, Union

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import to_hex

from python_toolkit.palettes.toolkit_palettes import (
    MATPLOTLIB_CATEGORICAL,
    MATPLOTLIB_COLOURBLIND_SAFE,
    MATPLOTLIB_CONTINUOUS,
    TOOLKIT_PALETTES,
)


class PaletteGroup(str, Enum):
    """The groups palettes are offered in."""

    CATEGORICAL = "categorical"
    CONTINUOUS = "continuous"
    COLOURBLIND = "colourblind"


def register_toolkit_palettes() -> None:
    """Register each toolkit palette, and its reversed `_r` copy, with matplotlib.

    A name that is already registered is left alone: where matplotlib provides a palette of the same
    name (e.g. `okabe_ito` from matplotlib 3.11), matplotlib's is used and the toolkit's is dropped.
    This also makes it safe to call more than once.
    """
    for palette in TOOLKIT_PALETTES:
        if palette.name in colormaps:
            continue
        cmap = palette.to_colormap()
        colormaps.register(cmap, name=palette.name)
        colormaps.register(cmap.reversed(), name=f"{palette.name}_r")


def palette_names(group: Optional[Union[PaletteGroup, str]] = None) -> list[str]:
    """List the palettes in a group.

    Args:
        group: The group to list. None lists every registered colour map, including the reversed `_r` copies.

    Returns:
        list[str]: Palette names; a group lists base palettes only, without the reversed copies.
    """
    if group is None:
        return sorted(colormaps, key=str.lower)
    return [name for name in _group_members(PaletteGroup(group)) if name in colormaps]


def is_categorical(name: str) -> bool:
    """Whether a palette, or its reversed copy, is categorical.

    Args:
        name: Palette name.

    Returns:
        bool: True if each colour of the palette is a separate category.
    """
    return name.removesuffix("_r") in _group_members(PaletteGroup.CATEGORICAL)


def sample_colours(name: str, count: int) -> list[str]:
    """Pick colours from a palette.

    Args:
        name: Palette name.
        count: Number of colours wanted.

    Returns:
        list[str]: `count` hex colours: the first ones of a categorical palette with enough colours,
            otherwise spread evenly from one end of the palette to the other.
    """
    cmap = colormaps[name]
    if is_categorical(name) and count <= cmap.N:
        positions = (np.arange(count) + 0.5) / cmap.N
    else:
        positions = np.linspace(0, 1, count) if count > 1 else [0.5]
    return [to_hex(cmap(position)) for position in positions]


def _group_members(group: PaletteGroup) -> list[str]:
    """The palette names in a group: matplotlib's, then the toolkit's own."""
    if group is PaletteGroup.CATEGORICAL:
        return [*MATPLOTLIB_CATEGORICAL, *(p.name for p in TOOLKIT_PALETTES if p.categorical)]
    if group is PaletteGroup.CONTINUOUS:
        return [*MATPLOTLIB_CONTINUOUS, *(p.name for p in TOOLKIT_PALETTES if not p.categorical)]
    return [*MATPLOTLIB_COLOURBLIND_SAFE, *(p.name for p in TOOLKIT_PALETTES if p.colourblind_safe)]
