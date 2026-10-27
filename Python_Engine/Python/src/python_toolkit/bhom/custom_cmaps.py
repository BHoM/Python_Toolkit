"""Persistence for user-defined colormaps.

Custom colormaps created via the CmapBuilder UI are stored in the colour scale library at
``~/.bhom/custom_cmaps.json`` (see ``python_toolkit.plot.colour_scales``) so they survive
across sessions and can be reloaded by any CmapSelector that opts in via ``allow_custom``.

These functions keep the original list-of-colormaps interface; new code should use
``ColourScaleLibrary`` directly, which keeps thresholds in data units and supports sets.
"""

from typing import List, Tuple

from matplotlib.colors import Colormap, LinearSegmentedColormap

from python_toolkit.plot.colour_scales import (
	ColourScaleLibrary,
	GradientScale,
	ThresholdScale,
)


# ------------------------------------------------------------------
# Internal helpers (mirror the builder's normalisation logic)
# ------------------------------------------------------------------

def _norm(val: float, vmin: float, vmax: float) -> float:
	span = vmax - vmin
	if span == 0:
		return 0.0
	return max(0.0, min(1.0, (val - vmin) / span))


def _build_interpolation_cmap(
	name: str,
	colours: list,
	positions: list,
	vmin: float,
	vmax: float,
) -> LinearSegmentedColormap:
	stops = sorted(
		((_norm(p, vmin, vmax), c) for p, c in zip(positions, colours)),
		key=lambda x: x[0],
	)
	return LinearSegmentedColormap.from_list(name, stops)


def _build_bins_cmap(
	name: str,
	colours: list,
	lower_bounds: list,
	vmin: float,
	vmax: float,
) -> LinearSegmentedColormap:
	paired = sorted(zip(lower_bounds, colours), key=lambda x: x[0])
	sorted_starts = [p[0] for p in paired]
	sorted_colours = [p[1] for p in paired]

	# End of each bin = start of the next; last bin always ends at vmax
	ends = sorted_starts[1:] + [vmax]
	norm_starts = [_norm(s, vmin, vmax) for s in sorted_starts]
	norm_ends = [_norm(e, vmin, vmax) for e in ends]
	norm_starts[0] = 0.0
	norm_ends[-1] = 1.0

	stops = []
	for i, colour in enumerate(sorted_colours):
		stops.append((norm_starts[i], colour))
		if i < len(sorted_colours) - 1:
			stops.append((norm_ends[i], colour))
	stops.append((1.0, sorted_colours[-1]))
	return LinearSegmentedColormap.from_list(name, stops)


def _as_colormap(scale) -> Tuple[Colormap, Tuple[float, float]]:
	"""A 0-1 colormap plus the data range it represents, for CmapSelector previews."""
	if isinstance(scale, ThresholdScale):
		preview = scale.preview_data()
		vmin, vmax = float(preview[0]), float(preview[-1])
		return _build_bins_cmap(scale.name, scale.colours, [vmin] + scale.thresholds, vmin, vmax), (vmin, vmax)
	positions = [p for p, _ in scale.stops]
	colours = [c for _, c in scale.stops]
	vmin, vmax = (0.0, 1.0) if scale.relative else (positions[0], positions[-1])
	return _build_interpolation_cmap(scale.name, colours, positions, vmin, vmax), (vmin, vmax)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def save_custom_cmap(
	name: str,
	cmap_type: str,
	colours: list,
	positions: list,
	vmin: float,
	vmax: float,
) -> None:
	"""Save or overwrite a custom colormap definition in the user file.

	Args:
		name: Display name for the colormap.
		cmap_type: ``"interpolation"`` or ``"bins"``.
		colours: Ordered list of hex colour strings.
		positions: For ``"interpolation"``: stop positions in data units.
			For ``"bins"``: lower boundary (start) of each bin in data units.
		vmin: Lower bound of the data range.
		vmax: Upper bound of the data range.
	"""
	if cmap_type == "bins":
		pairs = sorted(zip(positions, colours))
		scale = ThresholdScale(name, [p for p, _ in pairs[1:]], [c for _, c in pairs])
	else:
		scale = GradientScale(name, list(zip(positions, colours)), relative=False)
	ColourScaleLibrary().save(scale, overwrite=True)


def delete_custom_cmap(name: str) -> bool:
	"""Delete a single saved colormap by name.

	Returns:
		``True`` if the entry was found and removed, ``False`` otherwise.
	"""
	library = ColourScaleLibrary()
	if name not in library:
		return False
	library.delete(name)
	return True


def clear_custom_cmaps() -> None:
	"""Remove all saved custom colormaps."""
	ColourScaleLibrary().clear()


def list_custom_cmap_names() -> list:
	"""Return the names of all saved custom colormaps."""
	return ColourScaleLibrary().names()


def load_custom_cmaps() -> List[Tuple[str, Colormap, Tuple[float, float]]]:
	"""Load all user-defined colormaps.

	Returns:
		List of ``(name, colormap, (vmin, vmax))`` tuples. Entries that cannot be read
		are reported by the library (logged), not silently skipped.
	"""
	result = []
	for scale in ColourScaleLibrary().scales():
		cmap, bounds = _as_colormap(scale)
		result.append((scale.name, cmap, bounds))
	return result
