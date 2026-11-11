"""Colour scales: data split into bands at thresholds in data units, one colour per band.

    scale = ColourScale("Comfort", thresholds=[18, 21, 24], cmap="coolwarm", units="degC")
    cmap, norm = scale.cmap_and_norm(room_temperatures)
    save_scale(scale)

    suggest_thresholds(room_temperatures, bands=5, method="jenks")
"""

from python_toolkit.colour_scales.breaks import BreakMethod, suggest_thresholds
from python_toolkit.colour_scales.colour_scale import ColourScale
from python_toolkit.colour_scales.errors import ColourScaleError
from python_toolkit.colour_scales.library import DEFAULT_LIBRARY_PATH, delete_scale, load_scales, save_scale
from python_toolkit.colour_scales.values import finite_values

__all__ = [
    "BreakMethod",
    "ColourScale",
    "ColourScaleError",
    "DEFAULT_LIBRARY_PATH",
    "delete_scale",
    "finite_values",
    "load_scales",
    "save_scale",
    "suggest_thresholds",
]
