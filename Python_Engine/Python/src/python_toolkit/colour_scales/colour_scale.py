"""A colour scale: data split into bands at thresholds in data units, one colour per band."""

from typing import Any, Iterable, Optional, Sequence, Union

from matplotlib import colormaps
from matplotlib.colors import BoundaryNorm, ListedColormap, to_hex, to_rgba

from python_toolkit.colour_scales.errors import ColourScaleError
from python_toolkit.colour_scales.values import finite_values
from python_toolkit.palettes import sample_colours


class ColourScale:
    """A named set of bands split at thresholds in data units, coloured by a palette or explicit colours.

    A matplotlib Colormap only knows positions from 0 to 1, so a "18 / 21 / 24 degC" band set drifts
    whenever the data range changes. A ColourScale keeps its thresholds in data units, so it colours
    any data the same way:

        scale = ColourScale("Comfort", thresholds=[18, 21, 24], cmap="coolwarm",
                            labels=["Cold", "Cool", "Comfortable", "Hot"], units="degC")
        cmap, norm = scale.cmap_and_norm()
        ax.scatter(x, y, c=room_temperatures, cmap=cmap, norm=norm)
    """

    def __init__(
        self,
        name: str,
        thresholds: Sequence[float],
        cmap: Union[str, Sequence[str]] = "viridis",
        labels: Optional[Sequence[Optional[str]]] = None,
        units: Optional[str] = None,
    ) -> None:
        """
        Args:
            name: Name of the scale; must not be blank.
            thresholds: Band boundaries in data units, strictly increasing. N thresholds make N + 1 bands.
            cmap: A registered palette name, or one colour per band.
            labels: One legend label per band (None for the automatic range label), or None for all automatic.
            units: Units of the data the scale colours.

        Raises:
            ColourScaleError: If any argument is invalid.
        """
        self.name = (name or "").strip()
        if not self.name:
            raise ColourScaleError("A colour scale needs a name.")
        self.thresholds = [float(t) for t in thresholds]
        if not self.thresholds:
            raise ColourScaleError("A colour scale needs at least one threshold.")
        if any(upper <= lower for lower, upper in zip(self.thresholds, self.thresholds[1:])):
            raise ColourScaleError("Thresholds must be strictly increasing.")
        if labels is not None and len(labels) != self.band_count:
            raise ColourScaleError(f"Give one label per band ({self.band_count}), or none.")
        self.labels = [str(label) if label else None for label in labels] if labels is not None else None
        self.units = units
        self.cmap = cmap

    @property
    def band_count(self) -> int:
        """The number of bands: one more than the number of thresholds."""
        return len(self.thresholds) + 1

    @property
    def cmap(self) -> Union[str, list[str]]:
        """The palette name, or the explicit list of hex colours, one per band."""
        return self._cmap

    @cmap.setter
    def cmap(self, value: Union[str, Sequence[str]]) -> None:
        if isinstance(value, str):
            if value not in colormaps:
                raise ColourScaleError(f"Unknown colour map '{value}'.")
            self._cmap = value
            return
        colours = [_to_hex_colour(colour) for colour in value]
        if len(colours) != self.band_count:
            raise ColourScaleError(f"{len(self.thresholds)} threshold(s) make {self.band_count} bands, "
                                   f"but {len(colours)} colour(s) were given.")
        self._cmap = colours

    def colours(self) -> list[str]:
        """The colour of each band.

        Returns:
            list[str]: One hex colour per band.
        """
        if isinstance(self._cmap, str):
            return sample_colours(self._cmap, self.band_count)
        return list(self._cmap)

    def value_range(self, data: Optional[Iterable] = None) -> tuple[float, float]:
        """The range the scale spans.

        Args:
            data: Values the scale colours.

        Returns:
            tuple[float, float]: The data's minimum and maximum, or without data a span around the thresholds.
        """
        values = finite_values(data)
        if values.size:
            low, high = float(values.min()), float(values.max())
        else:
            pad = (self.thresholds[-1] - self.thresholds[0]) / max(self.band_count - 2, 1) or 1.0
            low, high = self.thresholds[0] - pad, self.thresholds[-1] + pad
        return (low - 0.5, high + 0.5) if low == high else (low, high)

    def cmap_and_norm(self, data: Optional[Iterable] = None) -> tuple[ListedColormap, BoundaryNorm]:
        """The matplotlib colour map and normaliser that colour data by this scale.

        Values beyond the end thresholds take the end colours. Pass the data so the end bands run to
        its minimum and maximum: a colour bar drawn with `spacing="proportional"` then shows every
        band at its true width.

        Args:
            data: Values the scale colours.

        Returns:
            tuple[ListedColormap, BoundaryNorm]: Pass both to a plot as `cmap` and `norm`.
        """
        low, high = self.value_range(data)
        t = self.thresholds
        first_gap, last_gap = (t[1] - t[0], t[-1] - t[-2]) if len(t) > 1 else (1.0, 1.0)
        lowest_edge = low if low < t[0] else t[0] - first_gap
        highest_edge = high if high > t[-1] else t[-1] + last_gap
        norm = BoundaryNorm([lowest_edge, *t, highest_edge], self.band_count, clip=True)
        return ListedColormap(self.colours(), name=self.name), norm

    def band_labels(self) -> list[str]:
        """The legend label of each band.

        Returns:
            list[str]: The given labels, with ranges such as '< 18', '18 - 21' and '>= 24' where none was given.
        """
        t = self.thresholds
        ranges = [f"< {_format_number(t[0])}"]
        ranges += [f"{_format_number(lower)} - {_format_number(upper)}" for lower, upper in zip(t, t[1:])]
        ranges += [f">= {_format_number(t[-1])}"]
        given = self.labels or [None] * len(ranges)
        return [label or default for label, default in zip(given, ranges)]

    def to_dict(self) -> dict[str, Any]:
        """The scale as a JSON-ready dictionary, the inverse of `from_dict`."""
        return {"name": self.name, "thresholds": self.thresholds, "cmap": self._cmap,
                "labels": self.labels, "units": self.units}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ColourScale":
        """Build a scale from a dictionary made by `to_dict`.

        Args:
            data: The saved scale. An older "colours" key is read in place of "cmap".

        Returns:
            ColourScale: The scale.

        Raises:
            KeyError: If a required key is missing.
            ColourScaleError: If the saved values are invalid.
        """
        return cls(data["name"], data["thresholds"], data.get("cmap") or data["colours"],
                   data.get("labels"), data.get("units"))

    def __repr__(self) -> str:
        return f"ColourScale({self.name!r}, thresholds={self.thresholds}, cmap={self._cmap!r})"


def _to_hex_colour(colour: str) -> str:
    """Convert any matplotlib colour to hex, raising ColourScaleError if it is not a colour."""
    try:
        return to_hex(to_rgba(colour))
    except ValueError as error:
        raise ColourScaleError(f"'{colour}' is not a colour.") from error


def _format_number(value: float) -> str:
    """Format a threshold to 4 significant figures for a label."""
    return f"{value:.4g}"
