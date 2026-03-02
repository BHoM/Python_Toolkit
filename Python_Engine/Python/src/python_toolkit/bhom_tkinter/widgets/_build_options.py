"""Typed build options shared by BHoM Tkinter widgets."""

from dataclasses import dataclass, asdict
from typing import Any, Literal

@dataclass
class BuildOptions:

    """Container for widget build options with type hints."""

    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary, excluding `None` values.

        Returns:
            dict: Build options filtered to keys with concrete values.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}