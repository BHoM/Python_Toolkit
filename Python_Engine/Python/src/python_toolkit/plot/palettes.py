"""Colour palettes: matplotlib's colour maps plus the toolkit's own, always registered.

Importing this module adds the toolkit palettes (and their reversed `_r` copies) to
matplotlib, so any palette name works anywhere a colour map name is accepted:

    palettes.names("colourblind")   # ['viridis', 'cividis', ..., 'okabe_ito']
    palettes.sample("okabe_ito", 4) # four hex colours
"""

from typing import List, Optional

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_hex

# The toolkit's own palettes: name -> (kind, colour-blind safe, colours).
CUSTOM = {
    "okabe_ito": ("categorical", True, ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]),
    "cool_to_warm": ("continuous", False, ["#3b4cc0", "#8db0fe", "#dddddd", "#f4987a", "#b40426"]),
    "traffic_light": ("continuous", False, ["#1a9850", "#fee08b", "#d73027"]),
    "ltc_heatmap": ("continuous", False, ["#000004", "#51127c", "#b63679", "#fb8861", "#fcffa4"]),
    "ltc_maya": ("continuous", False, ["#5c8286", "#a1b18c", "#e7cca6", "#d98f79", "#b35b5a"]),
    "ltc_paloma": ("continuous", False, ["#1a2a40", "#456a73", "#82a69d", "#d9ccb6", "#bf8865"]),
}

# matplotlib colour maps by kind; the toolkit palettes are added below.
KINDS = {
    "categorical": ["Accent", "Dark2", "Paired", "Pastel1", "Pastel2", "Set1", "Set2", "Set3",
                    "tab10", "tab20", "tab20b", "tab20c"],
    "continuous": ["viridis", "plasma", "inferno", "magma", "cividis", "turbo", "Blues", "Greens", "Greys",
                   "Oranges", "Purples", "Reds", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd", "coolwarm", "seismic",
                   "Spectral", "RdYlBu", "RdYlGn", "twilight", "twilight_shifted", "hsv"],
    # perceptually uniform maps; matplotlib's own, so safe for the common colour vision deficiencies
    "colourblind": ["viridis", "cividis", "plasma", "inferno", "magma"],
}

for _name, (_kind, _safe, _colours) in CUSTOM.items():
    if _name not in colormaps:
        _cmap = (ListedColormap(_colours, name=_name) if _kind == "categorical"
                 else LinearSegmentedColormap.from_list(_name, _colours))
        colormaps.register(_cmap, name=_name)
        colormaps.register(_cmap.reversed(), name=f"{_name}_r")
    KINDS[_kind].append(_name)
    if _safe:
        KINDS["colourblind"].append(_name)


def names(kind: Optional[str] = None) -> List[str]:
    """Colour map names of a kind ("categorical", "continuous", "colourblind"), without reversed copies.

    With no kind, every registered colour map including the reversed `_r` copies.
    """
    if kind is None:
        return sorted(colormaps, key=str.lower)
    return [name for name in KINDS[kind] if name in colormaps]


def sample(name: str, count: int) -> List[str]:
    """`count` hex colours from a palette: the first ones for a categorical palette, else evenly spread."""
    cmap = colormaps[name]
    base = name[:-2] if name.endswith("_r") else name
    if base in KINDS["categorical"] and count <= cmap.N:
        points = (np.arange(count) + 0.5) / cmap.N
    else:
        points = np.linspace(0, 1, count) if count > 1 else [0.5]
    return [to_hex(cmap(p)) for p in points]
