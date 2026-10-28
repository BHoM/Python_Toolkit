"""Colour scales defined in data units, with user-defined sets saved for reuse.

A matplotlib Colormap only knows positions from 0 to 1, so a saved "18 / 21 / 24 degC" band
set drifts whenever the data range changes. A ColourScale keeps its definition in data
units and produces the matching (Colormap, Normalize) pair for whatever data is passed in:

    scale = ThresholdScale("Comfort", thresholds=[18, 21, 24],
                           colours=["#3b4cc0", "#8db0fe", "#f4987a", "#b40426"],
                           labels=["Cold", "Cool", "Comfortable", "Hot"], units="degC")
    mapping = scale.mapping(room_temperatures)      # pass the data in
    ax.scatter(x, y, c=room_temperatures, cmap=mapping.cmap, norm=mapping.norm)

Scales can be suggested from the data (equal interval, quantile, or rounded "nice" breaks),
and are saved in a ColourScaleLibrary under named sets (e.g. "TM59", "Part L").
"""

from __future__ import annotations

import json
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Sequence, Tuple, Type

import numpy as np
from matplotlib import colormaps
from matplotlib.colors import (
    BoundaryNorm,
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    Normalize,
    to_hex,
    to_rgba,
)

from python_toolkit.bhom.logging import CONSOLE_LOGGER

LIBRARY_FILE = Path.home() / ".bhom" / "colour_scales.json"
LIBRARY_VERSION = 1
DEFAULT_SET = "My scales"

# Preset palettes for building scales (colour-blind safe sets first).
PALETTES: Dict[str, List[str]] = {
    "Okabe-Ito (colour-blind safe)": ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"],
    "Viridis (colour-blind safe)": ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"],
    "Cividis (colour-blind safe)": ["#00204c", "#31446b", "#666870", "#988e5d", "#ffe945"],
    "Cool to warm": ["#3b4cc0", "#8db0fe", "#dddddd", "#f4987a", "#b40426"],
    "Traffic light": ["#1a9850", "#fee08b", "#d73027"],
    "LTC Heatmap": ["#000004", "#51127c", "#b63679", "#fb8861", "#fcffa4"],
    "LTC Maya": ["#5c8286", "#a1b18c", "#e7cca6", "#d98f79", "#b35b5a"],
    "LTC Paloma": ["#1a2a40", "#456a73", "#82a69d", "#d9ccb6", "#bf8865"],
}

# Palettes registered as matplotlib colour maps (with _r), so every colour map list offers them.
# Viridis and Cividis are already matplotlib maps.
PALETTE_CMAPS: Dict[str, str] = {
    "Okabe-Ito (colour-blind safe)": "okabe_ito",
    "Cool to warm": "cool_to_warm",
    "Traffic light": "traffic_light",
    "LTC Heatmap": "ltc_heatmap",
    "LTC Maya": "ltc_maya",
    "LTC Paloma": "ltc_paloma",
}

SUGGESTION_METHODS = ("equal", "quantile", "nice")


class ColourScaleError(ValueError):
    """A colour scale definition, or the saved library, is invalid."""


# ---------------------------------------------------------------------------
# Data passed in
# ---------------------------------------------------------------------------

def clean_data(data: Optional[Iterable]) -> np.ndarray:
    """Finite float values from any iterable; None, NaN and non-numbers are dropped."""
    if data is None:
        return np.empty(0)
    numbers = np.array([_to_float(v) for v in np.ravel(np.asarray(list(data), dtype=object))], dtype=float)
    return numbers[np.isfinite(numbers)]


@dataclass(frozen=True)
class DataSummary:
    """What a scale needs to know about the data: range, spread and distribution."""

    count: int
    minimum: float
    maximum: float
    mean: float
    quartiles: Tuple[float, float, float]
    histogram: Tuple[np.ndarray, np.ndarray]  # (counts, bin edges)

    @classmethod
    def from_data(cls, data: Iterable, bins: int = 30) -> "DataSummary":
        values = clean_data(data)
        if values.size == 0:
            raise ColourScaleError("No numeric values in the data passed in.")
        lo, hi = float(values.min()), float(values.max())
        if lo == hi:
            lo, hi = lo - 0.5, hi + 0.5
        counts, edges = np.histogram(values, bins=bins, range=(lo, hi))
        q1, q2, q3 = (float(q) for q in np.quantile(values, [0.25, 0.5, 0.75]))
        return cls(int(values.size), float(values.min()), float(values.max()), float(values.mean()),
                   (q1, q2, q3), (counts, edges))


def suggest_thresholds(data: Iterable, bands: int, method: str = "nice") -> List[float]:
    """Inner boundaries splitting the data into `bands` bands.

    equal:    equal-width bands across the data range
    quantile: roughly the same number of values in each band
    nice:     equal-width bands on rounded 1 / 2 / 5 x 10^n steps
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

    return _nice_thresholds(lo, hi, bands - 1)


def _nice_thresholds(lo: float, hi: float, wanted: int) -> List[float]:
    """Rounded breaks (multiples of 1, 2, 2.5 or 5 x 10^n) strictly inside the data range.

    Picks the step whose breaks come closest to `wanted`, then keeps the middle `wanted`
    of them, so every band contains data rather than extending beyond it."""
    raw = (hi - lo) / (wanted + 1)
    exponent = math.floor(math.log10(raw))
    best = None
    for power in (exponent - 1, exponent, exponent + 1):
        for factor in (1, 2, 2.5, 5):
            step = factor * 10 ** power
            first, last = math.floor(lo / step) + 1, math.ceil(hi / step) - 1
            inner = [round(k * step, 10) for k in range(first, last + 1)]
            if not inner:
                continue
            score = abs(len(inner) - wanted) + (0.5 if factor == 2.5 else 0.0)  # prefer rounder steps
            if best is None or score < best[0]:
                best = (score, inner)
    if best is None:  # range too narrow for rounded breaks
        return [float(v) for v in np.linspace(lo, hi, wanted + 2)[1:-1]]
    inner = best[1]
    if len(inner) > wanted:
        start = (len(inner) - wanted) // 2
        inner = inner[start:start + wanted]
    return inner


def register_palette_cmaps() -> None:
    """Add the preset palettes to matplotlib's colour maps (idempotent)."""
    for palette, name in PALETTE_CMAPS.items():
        if name not in colormaps:
            cmap = LinearSegmentedColormap.from_list(name, PALETTES[palette])
            colormaps.register(cmap, name=name)
            colormaps.register(cmap.reversed(), name=f"{name}_r")


def palette_names() -> List[str]:
    """Preset palettes first, then every matplotlib colour map (no reversed copies)."""
    preset = set(PALETTE_CMAPS.values())
    return list(PALETTES) + sorted((n for n in colormaps if not n.endswith("_r") and n not in preset), key=str.lower)


def palette_colours(palette: str, count: int) -> List[str]:
    """`count` colours sampled evenly from a preset palette or a matplotlib colour map."""
    if palette in PALETTES:
        cmap = LinearSegmentedColormap.from_list(palette, PALETTES[palette])
    elif palette in colormaps:
        cmap = colormaps[palette]
    else:
        raise ColourScaleError(f"Unknown palette or colour map '{palette}'.")
    if count == 1:
        return [to_hex(cmap(0.5))]
    return [to_hex(cmap(i / (count - 1))) for i in range(count)]


# ---------------------------------------------------------------------------
# Scales
# ---------------------------------------------------------------------------

@dataclass
class ScaleMapping:
    """Everything a plot needs to colour values with a scale."""

    cmap: Colormap
    norm: Normalize
    ticks: List[float]
    tick_labels: List[str]
    band_labels: Optional[List[str]] = None  # threshold scales: one per band, for legends

    def colours_for(self, values: Iterable) -> np.ndarray:
        """RGBA per value (NaN for values that cannot be read)."""
        data = np.array([_to_float(v) for v in values], dtype=float)
        out = np.full((data.size, 4), np.nan)
        ok = np.isfinite(data)
        if ok.any():
            out[ok] = self.cmap(self.norm(data[ok]))
        return out


class ColourScale(ABC):
    """Base class: a named colour scale defined in data units.

    Subclasses produce a ScaleMapping from the data passed in, and round-trip through
    plain dicts so they can be saved. `group` is the user-defined set the scale belongs to.
    """

    kind: ClassVar[str] = ""
    _registry: ClassVar[Dict[str, Type["ColourScale"]]] = {}

    def __init__(self, name: str, units: Optional[str] = None, description: str = "",
                 group: str = DEFAULT_SET):
        self.name = validate_name(name)
        self.units = units
        self.description = description
        self.group = group or DEFAULT_SET

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.kind:
            ColourScale._registry[cls.kind] = cls

    @abstractmethod
    def mapping(self, data: Optional[Iterable] = None) -> ScaleMapping:
        """Colormap and normaliser for this scale, fitted to `data` where the scale is relative."""

    @abstractmethod
    def _definition(self) -> Dict[str, Any]:
        """Subclass-specific fields for to_dict."""

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.kind, "name": self.name, "units": self.units,
                "description": self.description, "group": self.group, **self._definition()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ColourScale":
        kind = data.get("type")
        scale_cls = ColourScale._registry.get(kind)
        if scale_cls is None:
            raise ColourScaleError(f"Unknown colour scale type '{kind}'.")
        return scale_cls._from_definition(data)

    @classmethod
    @abstractmethod
    def _from_definition(cls, data: Dict[str, Any]) -> "ColourScale":
        """Build from a dict written by to_dict."""

    def preview_data(self) -> np.ndarray:
        """Representative values spanning the scale, for swatches without real data."""
        return np.linspace(0.0, 1.0, 11)

    def to_colormap(self, data: Optional[Iterable] = None, samples: int = 256) -> Colormap:
        """A plain 0-1 colormap that looks like this scale across its range (band widths kept),
        for widgets that only take a Colormap. Plots should use `mapping`, which keeps data units."""
        mapping = self.mapping(data if data is not None else self.preview_data())
        values = np.linspace(mapping.norm.vmin, mapping.norm.vmax, samples)
        return ListedColormap(mapping.cmap(mapping.norm(values)), name=self.name)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r}, set={self.group!r})"


class GradientScale(ColourScale):
    """A continuous gradient through colour stops.

    Stop positions are either absolute data values, or relative (0 = data minimum,
    1 = data maximum) so the gradient stretches to whatever data is passed in.
    """

    kind = "gradient"

    def __init__(self, name: str, stops: Sequence[Tuple[float, str]], relative: bool = True,
                 bins: Optional[int] = None, **kwargs):
        super().__init__(name, **kwargs)
        if len(stops) < 2:
            raise ColourScaleError("A gradient needs at least 2 colour stops.")
        self.stops = sorted(((float(p), _hex(c)) for p, c in stops), key=lambda s: s[0])
        self.relative = bool(relative)
        self.bins = bins  # None for smooth, or a number of discrete steps
        positions = [p for p, _ in self.stops]
        if positions[0] == positions[-1]:
            raise ColourScaleError("Gradient stops must span a range.")
        if self.relative and (positions[0] < 0 or positions[-1] > 1):
            raise ColourScaleError("Relative stop positions must lie between 0 and 1.")

    @classmethod
    def from_palette(cls, name: str, palette: str, **kwargs) -> "GradientScale":
        if palette not in PALETTES:
            raise ColourScaleError(f"Unknown palette '{palette}'.")
        colours = PALETTES[palette]
        n = len(colours)
        return cls(name, [(i / (n - 1), c) for i, c in enumerate(colours)], relative=True, **kwargs)

    def value_range(self, data: Optional[Iterable] = None) -> Tuple[float, float]:
        if not self.relative:
            return self.stops[0][0], self.stops[-1][0]
        values = clean_data(data)
        if values.size == 0:
            return 0.0, 1.0
        lo, hi = float(values.min()), float(values.max())
        return (lo - 0.5, hi + 0.5) if lo == hi else (lo, hi)

    def mapping(self, data: Optional[Iterable] = None) -> ScaleMapping:
        vmin, vmax = self.value_range(data)
        first, last = self.stops[0][0], self.stops[-1][0]
        nodes = [((p - first) / (last - first), c) for p, c in self.stops]
        cmap = LinearSegmentedColormap.from_list(self.name, nodes)
        if self.bins:
            cmap = cmap.resampled(int(self.bins))
            edges = list(np.linspace(vmin, vmax, int(self.bins) + 1))
            norm = BoundaryNorm(edges, ncolors=int(self.bins), clip=True)
            ticks = edges
        else:
            norm = Normalize(vmin=vmin, vmax=vmax, clip=True)
            ticks = list(np.linspace(vmin, vmax, 6))
        return ScaleMapping(cmap, norm, ticks, [_fmt(t) for t in ticks])

    def _definition(self) -> Dict[str, Any]:
        return {"stops": [[p, c] for p, c in self.stops], "relative": self.relative, "bins": self.bins}

    @classmethod
    def _from_definition(cls, data: Dict[str, Any]) -> "GradientScale":
        return cls(data["name"], [tuple(s) for s in data["stops"]], relative=data.get("relative", True),
                   bins=data.get("bins"), units=data.get("units"), description=data.get("description", ""),
                   group=data.get("group") or DEFAULT_SET)


class ThresholdScale(ColourScale):
    """Bands with fixed boundaries in data units: one colour (and optional label) per band.

    `thresholds` are the inner boundaries; values below the first threshold take the first
    colour and values at or above the last take the last, so the bands hold for any data.
    """

    kind = "thresholds"

    def __init__(self, name: str, thresholds: Sequence[float], colours: Sequence[str],
                 labels: Optional[Sequence[Optional[str]]] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.thresholds = [float(t) for t in thresholds]
        self.colours = [_hex(c) for c in colours]
        if not self.thresholds:
            raise ColourScaleError("A threshold scale needs at least one threshold.")
        if any(b <= a for a, b in zip(self.thresholds, self.thresholds[1:])):
            raise ColourScaleError("Thresholds must be strictly increasing.")
        if len(self.colours) != len(self.thresholds) + 1:
            raise ColourScaleError(
                f"{len(self.thresholds)} threshold(s) make {len(self.thresholds) + 1} bands, "
                f"but {len(self.colours)} colour(s) were given.")
        if labels is not None and len(labels) != len(self.colours):
            raise ColourScaleError(f"Give one label per band ({len(self.colours)}), or none.")
        self.labels = [None if not l else str(l) for l in labels] if labels is not None else None

    @classmethod
    def from_data(cls, name: str, data: Iterable, bands: int = 5, method: str = "nice",
                  palette: str = "Viridis (colour-blind safe)", **kwargs) -> "ThresholdScale":
        """Suggest thresholds from the data passed in, coloured from a preset palette."""
        thresholds = suggest_thresholds(data, bands, method)
        return cls(name, thresholds, palette_colours(palette, len(thresholds) + 1), **kwargs)

    @property
    def bands(self) -> int:
        return len(self.colours)

    def band_ranges(self) -> List[Tuple[Optional[float], Optional[float]]]:
        """(lower, upper) per band; None for the open ends."""
        edges: List[Optional[float]] = [None] + list(self.thresholds) + [None]
        return list(zip(edges[:-1], edges[1:]))

    def band_labels(self) -> List[str]:
        """Labels as given, else ranges such as '< 18', '18 - 21', '>= 24'."""
        auto = []
        for lower, upper in self.band_ranges():
            if lower is None:
                auto.append(f"< {_fmt(upper)}")
            elif upper is None:
                auto.append(f">= {_fmt(lower)}")
            else:
                auto.append(f"{_fmt(lower)} - {_fmt(upper)}")
        if self.labels is None:
            return auto
        return [given or default for given, default in zip(self.labels, auto)]

    def band_of(self, value: float) -> int:
        """Index of the band a value falls in."""
        return int(np.searchsorted(self.thresholds, float(value), side="right"))

    def mapping(self, data: Optional[Iterable] = None) -> ScaleMapping:
        values = clean_data(data)
        span = self.thresholds[-1] - self.thresholds[0] or 1.0
        lo = min(self.thresholds[0] - span / max(self.bands - 2, 1), float(values.min()) if values.size else math.inf)
        hi = max(self.thresholds[-1] + span / max(self.bands - 2, 1), float(values.max()) if values.size else -math.inf)
        edges = [lo] + self.thresholds + [hi + 1e-9]
        cmap = ListedColormap(self.colours, name=self.name)
        norm = BoundaryNorm(edges, ncolors=self.bands, clip=True)
        return ScaleMapping(cmap, norm, list(self.thresholds), [_fmt(t) for t in self.thresholds],
                            band_labels=self.band_labels())

    def preview_data(self) -> np.ndarray:
        span = self.thresholds[-1] - self.thresholds[0] or 1.0
        pad = span / max(self.bands - 2, 1)
        return np.linspace(self.thresholds[0] - pad, self.thresholds[-1] + pad, 101)

    def _definition(self) -> Dict[str, Any]:
        return {"thresholds": self.thresholds, "colours": self.colours, "labels": self.labels}

    @classmethod
    def _from_definition(cls, data: Dict[str, Any]) -> "ThresholdScale":
        return cls(data["name"], data["thresholds"], data["colours"], labels=data.get("labels"),
                   units=data.get("units"), description=data.get("description", ""),
                   group=data.get("group") or DEFAULT_SET)


# ---------------------------------------------------------------------------
# Library: saved scales grouped in user-defined sets
# ---------------------------------------------------------------------------

class ColourScaleLibrary:
    """Saved colour scales, grouped into named sets, stored as JSON.

    Entries that cannot be read are kept on disk, reported in `problems` and logged,
    never silently dropped.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else LIBRARY_FILE
        self.problems: List[str] = []
        self._scales: Dict[str, ColourScale] = {}
        self._unreadable: List[Dict[str, Any]] = []
        self.reload()

    def reload(self) -> None:
        self._scales.clear()
        self._unreadable.clear()
        self.problems = []
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise ColourScaleError(f"Cannot read the colour scale library {self.path}: {e}") from e

        entries = raw.get("scales", []) if isinstance(raw, dict) else raw
        if not isinstance(entries, list):
            raise ColourScaleError(f"{self.path} is not a colour scale library.")
        for entry in entries:
            try:
                scale = ColourScale.from_dict(entry)
            except (KeyError, TypeError, ValueError) as e:
                name = entry.get("name", "?") if isinstance(entry, dict) else "?"
                self.problems.append(f"Could not read saved scale '{name}': {e}")
                self._unreadable.append(entry)
                continue
            self._scales[scale.name] = scale
        for problem in self.problems:
            CONSOLE_LOGGER.warning(problem)

    # -- queries ------------------------------------------------------------

    def names(self, group: Optional[str] = None) -> List[str]:
        return [s.name for s in self._scales.values() if group is None or s.group == group]

    def groups(self) -> List[str]:
        """The user-defined sets, in first-seen order."""
        return list(dict.fromkeys(s.group for s in self._scales.values()))

    def scales(self, group: Optional[str] = None) -> List[ColourScale]:
        return [s for s in self._scales.values() if group is None or s.group == group]

    def get(self, name: str) -> ColourScale:
        if name not in self._scales:
            raise KeyError(f"No saved colour scale named '{name}'.")
        return self._scales[name]

    def __contains__(self, name: str) -> bool:
        return name in self._scales

    def __len__(self) -> int:
        return len(self._scales)

    # -- changes ------------------------------------------------------------

    def save(self, scale: ColourScale, overwrite: bool = False) -> None:
        if scale.name in self._scales and not overwrite:
            raise ColourScaleError(f"A scale named '{scale.name}' already exists.")
        self._scales[scale.name] = scale
        self._write()

    def delete(self, name: str) -> None:
        if name not in self._scales:
            raise KeyError(f"No saved colour scale named '{name}'.")
        del self._scales[name]
        self._write()

    def rename_group(self, old: str, new: str) -> None:
        for scale in self.scales(old):
            scale.group = new
        self._write()

    def delete_group(self, group: str) -> None:
        for name in self.names(group):
            del self._scales[name]
        self._write()

    def clear(self) -> None:
        self._scales.clear()
        self._write()

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": LIBRARY_VERSION,
                   "scales": [s.to_dict() for s in self._scales.values()] + self._unreadable}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self.path)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_INVALID_NAME_CHARS = set(r'\/:*?"<>|')


def validate_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        raise ColourScaleError("A colour scale needs a name.")
    if any(c in _INVALID_NAME_CHARS for c in name):
        raise ColourScaleError("Names cannot contain \\ / : * ? \" < > |")
    return name


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


register_palette_cmaps()
