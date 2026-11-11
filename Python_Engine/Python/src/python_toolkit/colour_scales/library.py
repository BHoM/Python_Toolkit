"""The saved colour scales file: one JSON file, one entry per scale name."""

import json
from pathlib import Path
from typing import Any, Optional

from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.colour_scales.colour_scale import ColourScale
from python_toolkit.colour_scales.errors import ColourScaleError

DEFAULT_LIBRARY_PATH = Path.home() / ".bhom" / "colour_scales.json"


def load_scales(path: Optional[Path] = None) -> list[ColourScale]:
    """Read the saved scales.

    Args:
        path: The saved scales file; defaults to DEFAULT_LIBRARY_PATH.

    Returns:
        list[ColourScale]: The saved scales. Entries that cannot be read are logged and skipped,
            but never removed from the file.

    Raises:
        ColourScaleError: If the file cannot be read or is not a saved scales file.
    """
    scales = []
    for entry in _read_entries(path):
        try:
            scales.append(ColourScale.from_dict(entry))
        except (KeyError, TypeError, ValueError) as error:
            CONSOLE_LOGGER.warning(f"Could not read saved scale '{entry.get('name', '?')}': {error}")
    return scales


def save_scale(scale: ColourScale, path: Optional[Path] = None, overwrite: bool = False,
               replaces: Optional[str] = None) -> None:
    """Add a scale to the saved scales file.

    Args:
        scale: The scale to save.
        path: The saved scales file; defaults to DEFAULT_LIBRARY_PATH.
        overwrite: Replace a saved scale of the same name.
        replaces: The saved name this scale is an edit of. That entry is replaced without needing
            `overwrite`, so a renamed scale does not leave its old name behind.

    Raises:
        ColourScaleError: If a different scale of the same name is saved and `overwrite` is False.
    """
    entries = _read_entries(path)
    name_taken = scale.name != replaces and any(entry.get("name") == scale.name for entry in entries)
    if name_taken and not overwrite:
        raise ColourScaleError(f"A scale named '{scale.name}' already exists.")
    others = [entry for entry in entries if entry.get("name") not in (scale.name, replaces)]
    _write_entries(path, [*others, scale.to_dict()])


def delete_scale(name: str, path: Optional[Path] = None) -> bool:
    """Remove a saved scale.

    Args:
        name: Name of the scale to remove.
        path: The saved scales file; defaults to DEFAULT_LIBRARY_PATH.

    Returns:
        bool: True if a scale was removed, False if none had that name.
    """
    entries = _read_entries(path)
    others = [entry for entry in entries if entry.get("name") != name]
    if len(others) == len(entries):
        return False
    _write_entries(path, others)
    return True


def _read_entries(path: Optional[Path]) -> list[dict[str, Any]]:
    """The raw scale entries in the file, or [] if there is no file yet."""
    path = Path(path or DEFAULT_LIBRARY_PATH)
    if not path.exists():
        return []
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ColourScaleError(f"Cannot read the colour scale library {path}: {error}") from error
    entries = content.get("scales") if isinstance(content, dict) else content
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ColourScaleError(f"{path} is not a colour scale library.")
    return entries


def _write_entries(path: Optional[Path], entries: list[dict[str, Any]]) -> None:
    """Write the scale entries, via a temporary file so a failed write cannot corrupt the library."""
    path = Path(path or DEFAULT_LIBRARY_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"version": 1, "scales": entries}, indent=2), encoding="utf-8")
    temporary.replace(path)
