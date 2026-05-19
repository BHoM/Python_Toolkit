"""Persistence for user-defined colormaps.

Custom colormaps created via the CmapBuilder UI are stored as JSON at
``~/.bhom/custom_cmaps.json`` so they survive across sessions and can be
reloaded by any CmapSelector that opts in via ``load_custom=True``.
"""

import json
from pathlib import Path
from typing import Optional

from matplotlib.colors import LinearSegmentedColormap

_USER_CMAPS_DIR = Path.home() / ".bhom"
_USER_CMAPS_FILE = _USER_CMAPS_DIR / "custom_cmaps.json"


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
		positions: For ``"interpolation"``: normalised stop positions.
			For ``"bins"``: lower boundary (start) of each bin in data units.
		vmin: Lower bound of the data range.
		vmax: Upper bound of the data range.
	"""
	_USER_CMAPS_DIR.mkdir(parents=True, exist_ok=True)

	entries: list = []
	if _USER_CMAPS_FILE.exists():
		try:
			with _USER_CMAPS_FILE.open("r", encoding="utf-8") as fh:
				entries = json.load(fh)
			if not isinstance(entries, list):
				entries = []
		except Exception:
			entries = []

	entry = {
		"name": name,
		"type": cmap_type,
		"vmin": vmin,
		"vmax": vmax,
		"colours": colours,
		"positions": positions,
	}

	# Replace existing entry with the same name, otherwise append.
	for i, existing in enumerate(entries):
		if existing.get("name") == name:
			entries[i] = entry
			break
	else:
		entries.append(entry)

	with _USER_CMAPS_FILE.open("w", encoding="utf-8") as fh:
		json.dump(entries, fh, indent=2)


def delete_custom_cmap(name: str) -> bool:
	"""Delete a single saved colormap by name.

	Args:
		name: The name of the colormap to remove.

	Returns:
		``True`` if the entry was found and removed, ``False`` otherwise.
	"""
	if not _USER_CMAPS_FILE.exists():
		return False
	try:
		with _USER_CMAPS_FILE.open("r", encoding="utf-8") as fh:
			entries = json.load(fh)
		if not isinstance(entries, list):
			return False
		filtered = [e for e in entries if e.get("name") != name]
		if len(filtered) == len(entries):
			return False
		with _USER_CMAPS_FILE.open("w", encoding="utf-8") as fh:
			json.dump(filtered, fh, indent=2)
		return True
	except Exception:
		return False


def clear_custom_cmaps() -> None:
	"""Remove all saved custom colormaps (writes an empty list to the file)."""
	if not _USER_CMAPS_FILE.exists():
		return
	try:
		with _USER_CMAPS_FILE.open("w", encoding="utf-8") as fh:
			json.dump([], fh, indent=2)
	except Exception:
		pass


def list_custom_cmap_names() -> list:
	"""Return the names of all saved custom colormaps.

	Returns:
		Ordered list of name strings.
	"""
	if not _USER_CMAPS_FILE.exists():
		return []
	try:
		with _USER_CMAPS_FILE.open("r", encoding="utf-8") as fh:
			entries = json.load(fh)
		if not isinstance(entries, list):
			return []
		return [str(e["name"]) for e in entries if "name" in e]
	except Exception:
		return []


def load_custom_cmaps() -> list:
	"""Load all user-defined colormaps from the user file.

	Returns:
		List of ``(name, colormap, (vmin, vmax))`` tuples.  Entries that
		cannot be reconstructed are silently skipped.
	"""
	if not _USER_CMAPS_FILE.exists():
		return []

	try:
		with _USER_CMAPS_FILE.open("r", encoding="utf-8") as fh:
			entries = json.load(fh)
		if not isinstance(entries, list):
			return []
	except Exception:
		return []

	result = []
	for entry in entries:
		try:
			name = str(entry["name"])
			cmap_type = str(entry.get("type", "interpolation"))
			vmin = float(entry["vmin"])
			vmax = float(entry["vmax"])
			colours = list(entry["colours"])
			positions = list(entry["positions"])

			if cmap_type == "bins":
				cmap = _build_bins_cmap(name, colours, positions, vmin, vmax)
			else:
				cmap = _build_interpolation_cmap(name, colours, positions, vmin, vmax)

			result.append((name, cmap, (vmin, vmax)))
		except Exception:
			continue

	return result
