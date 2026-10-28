"""Colour scales: data broken into bands at thresholds in data units, coloured by a palette.

A matplotlib Colormap only knows positions from 0 to 1, so a saved "18 / 21 / 24 degC" band
set drifts whenever the data range changes. A ColourScale keeps its thresholds in data units
and produces the matching (Colormap, Normalize) pair, whatever data it is used on:

    scale = ColourScale("Comfort", thresholds=[18, 21, 24], cmap="coolwarm",
                        labels=["Cold", "Cool", "Comfortable", "Hot"], units="degC")
    cmap, norm = scale.mapping()
    ax.scatter(x, y, c=room_temperatures, cmap=cmap, norm=norm)
    scale.cmap = "okabe_ito"            # the colours can change; the thresholds stay

`cmap` is a palette name (see `python_toolkit.plot.palettes`) or an explicit list of colours,
one per band.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import BoundaryNorm, Colormap, ListedColormap, to_hex, to_rgba

from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.plot import palettes

LIBRARY_FILE = Path.home() / ".bhom" / "colour_scales.json"
SUGGESTION_METHODS = ("equal", "quantile", "nice", "log")


class ColourScaleError(ValueError):
    """A colour scale definition, or the saved library, is invalid."""


class ColourScale:
    """A named set of bands split at `thresholds` (data units), coloured by `cmap`."""

    def __init__(self, name: str, thresholds: Sequence[float], cmap: Union[str, Sequence[str]] = "viridis",
                 labels: Optional[Sequence[Optional[str]]] = None, units: Optional[str] = None):
        self.name = (name or "").strip()
        if not self.name:
            raise ColourScaleError("A colour scale needs a name.")
        self.thresholds = [float(t) for t in thresholds]
        if not self.thresholds:
            raise ColourScaleError("A colour scale needs at least one threshold.")
        if any(b <= a for a, b in zip(self.thresholds, self.thresholds[1:])):
            raise ColourScaleError("Thresholds must be strictly increasing.")
        if labels is not None and len(labels) != self.bands:
            raise ColourScaleError(f"Give one label per band ({self.bands}), or none.")
        self.labels = [str(l) if l else None for l in labels] if labels is not None else None
        self.units = units
        self.cmap = cmap

    @property
    def bands(self) -> int:
        return len(self.thresholds) + 1

    @property
    def cmap(self) -> Union[str, List[str]]:
        return self._cmap

    @cmap.setter
    def cmap(self, value: Union[str, Sequence[str]]) -> None:
        if isinstance(value, str):
            if value not in colormaps:
                raise ColourScaleError(f"Unknown colour map '{value}'.")
            self._cmap = value
            return
        colours = [_hex(c) for c in value]
        if len(colours) != self.bands:
            raise ColourScaleError(f"{len(self.thresholds)} threshold(s) make {self.bands} bands, "
                                   f"but {len(colours)} colour(s) were given.")
        self._cmap = colours

    def colours(self) -> List[str]:
        """One hex colour per band."""
        return list(self._cmap) if not isinstance(self._cmap, str) else palettes.sample(self._cmap, self.bands)

    def value_range(self, data: Optional[Iterable] = None) -> Tuple[float, float]:
        """The data range, or a span around the thresholds without data."""
        values = clean_data(data)
        if values.size:
            lo, hi = float(values.min()), float(values.max())
        else:
            pad = (self.thresholds[-1] - self.thresholds[0]) / max(self.bands - 2, 1) or 1.0
            lo, hi = self.thresholds[0] - pad, self.thresholds[-1] + pad
        return (lo - 0.5, hi + 0.5) if lo == hi else (lo, hi)

    def mapping(self) -> Tuple[Colormap, BoundaryNorm]:
        """The colormap and normaliser to colour any data with; values beyond the ends take the end colours."""
        edges = [self.thresholds[0] - 1] + self.thresholds + [self.thresholds[-1] + 1]
        return ListedColormap(self.colours(), name=self.name), BoundaryNorm(edges, self.bands, clip=True)

    def band_labels(self) -> List[str]:
        """Labels as given, else ranges such as '< 18', '18 - 21', '>= 24'."""
        t = self.thresholds
        auto = [f"< {_fmt(t[0])}"] + [f"{_fmt(a)} - {_fmt(b)}" for a, b in zip(t, t[1:])] + [f">= {_fmt(t[-1])}"]
        given = self.labels or [None] * len(auto)
        return [g or a for g, a in zip(given, auto)]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "thresholds": self.thresholds, "cmap": self._cmap,
                "labels": self.labels, "units": self.units}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColourScale":
        # "colours" is the older name for the colour list
        return cls(data["name"], data["thresholds"], data.get("cmap") or data["colours"],
                   data.get("labels"), data.get("units"))

    def __repr__(self) -> str:
        return f"ColourScale({self.name!r}, thresholds={self.thresholds}, cmap={self._cmap!r})"


# ---------------------------------------------------------------------------
# Suggesting thresholds from data
# ---------------------------------------------------------------------------

def suggest_thresholds(data: Iterable, bands: int, method: str = "nice") -> List[float]:
    """Inner boundaries splitting the data into `bands` bands.

    equal:    equal-width bands across the data range
    quantile: roughly the same number of values in each band
    nice:     equal-width bands on rounded 1 / 2 / 5 x 10^n steps
    log:      bands of equal ratio (each break a fixed multiple of the last), rounded to 3 significant
              figures; needs every value above zero
    """
    if bands < 2:
        raise ColourScaleError("A threshold scale needs at least 2 bands.")
    if method not in SUGGESTION_METHODS:
        raise ColourScaleError(f"Method must be one of {SUGGESTION_METHODS}, not '{method}'.")
    values = clean_data(data)
    if values.size == 0:
        raise ColourScaleError("No numeric values to suggest thresholds from.")
    lo, hi = float(values.min()), float(values.max())
    if lo == hi:
        return [lo + i for i in range(1, bands)]

    if method == "equal":
        return [float(v) for v in np.linspace(lo, hi, bands + 1)[1:-1]]
    if method == "quantile":
        cuts = np.quantile(values, np.linspace(0, 1, bands + 1)[1:-1])
        unique = sorted(set(float(c) for c in cuts))
        if len(unique) < bands - 1:
            raise ColourScaleError("Too many repeated values for that many quantile bands; use fewer bands.")
        return unique
    if method == "log":
        if lo <= 0:
            raise ColourScaleError("Logarithmic breaks need every value above zero; use another break method.")
        cuts = [float(f"{v:.3g}") for v in np.geomspace(lo, hi, bands + 1)[1:-1]]
        if any(b <= a for a, b in zip(cuts, cuts[1:])) or cuts[0] <= lo or cuts[-1] >= hi:
            raise ColourScaleError("The data range is too narrow for that many logarithmic bands; use fewer bands.")
        return cuts
    return _nice_thresholds(lo, hi, bands - 1)


def _nice_thresholds(lo: float, hi: float, wanted: int) -> List[float]:
    """Rounded breaks (multiples of 1, 2, 2.5 or 5 x 10^n) strictly inside the data range.

    Picks the step with the fewest breaks that is still at least `wanted`, then keeps the middle `wanted`
    of them, so every band contains data rather than extending beyond it."""
    exponent = math.floor(math.log10((hi - lo) / (wanted + 1)))
    best = None
    for power in (exponent - 1, exponent, exponent + 1):
        for factor in (1, 2, 2.5, 5):
            step = factor * 10 ** power
            inner = [round(k * step, 10) for k in range(math.floor(lo / step) + 1, math.ceil(hi / step))]
            if len(inner) < wanted:  # always return the number of breaks asked for
                continue
            score = abs(len(inner) - wanted) + (0.5 if factor == 2.5 else 0.0)  # prefer rounder steps
            if best is None or score < best[0]:
                best = (score, inner)
    if best is None:  # range too narrow for rounded breaks
        return [float(v) for v in np.linspace(lo, hi, wanted + 2)[1:-1]]
    inner = best[1]
    start = max(len(inner) - wanted, 0) // 2
    return inner[start:start + wanted]


# ---------------------------------------------------------------------------
# Saved scales: one JSON file, one entry per name
# ---------------------------------------------------------------------------

def load_scales(path: Optional[Path] = None) -> List[ColourScale]:
    """Saved scales; entries that cannot be read are logged and skipped (never deleted from the file)."""
    scales = []
    for entry in _read(path):
        try:
            scales.append(ColourScale.from_dict(entry))
        except (KeyError, TypeError, ValueError) as e:
            CONSOLE_LOGGER.warning(f"Could not read saved scale '{entry.get('name', '?')}': {e}")
    return scales


def save_scale(scale: ColourScale, path: Optional[Path] = None, overwrite: bool = False) -> None:
    """Add a scale to the saved file; an existing name is only replaced with `overwrite`."""
    path = Path(path or LIBRARY_FILE)
    entries = _read(path)
    others = [e for e in entries if e.get("name") != scale.name]
    if len(others) < len(entries) and not overwrite:
        raise ColourScaleError(f"A scale named '{scale.name}' already exists.")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": 1, "scales": others + [scale.to_dict()]}, indent=2), encoding="utf-8")
    tmp.replace(path)


def _read(path: Optional[Path]) -> List[Dict[str, Any]]:
    path = Path(path or LIBRARY_FILE)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ColourScaleError(f"Cannot read the colour scale library {path}: {e}") from e
    entries = raw.get("scales") if isinstance(raw, dict) else raw
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise ColourScaleError(f"{path} is not a colour scale library.")
    return entries


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_data(data: Optional[Iterable]) -> np.ndarray:
    """Finite float values from any iterable; None, NaN and non-numbers are dropped."""
    if data is None:
        return np.empty(0)
    numbers = np.array([_to_float(v) for v in np.ravel(np.asarray(list(data), dtype=object))], dtype=float)
    return numbers[np.isfinite(numbers)]


def _hex(colour: str) -> str:
    try:
        return to_hex(to_rgba(colour))
    except ValueError as e:
        raise ColourScaleError(f"'{colour}' is not a colour.") from e


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def _fmt(value: float) -> str:
    return f"{value:.4g}"
