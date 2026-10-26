"""Typed gridding options shared by BHoM Tkinter widgets."""

from dataclasses import dataclass, asdict
from typing import Any, Literal

from python_toolkit.bhom_tkinter.widgets._build_options import BuildOptions
from python_toolkit.bhom_tkinter.theming.scaling import scale, scale_pad

@dataclass
class GridOptions(BuildOptions):

    """Container for `grid` geometry keyword arguments with type hints."""

    column: int = 0
    columnspan: int = 1
    in_: Any = None
    ipadx: float | str = 0.0
    ipady: float | str = 0.0
    padx: float | str | tuple[float | str, float | str] = 0.0
    pady: float | str | tuple[float | str, float | str] = 0.0
    row: int = 0
    rowspan: int = 1
    sticky: Literal['n', 'e', 's', 'w', 'ne', 'nw', 'se', 'sw', ''] = ''

    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary, excluding `None` values.

        Returns:
            dict: Gridding options filtered to keys with concrete values.
        """
        options = {k: v for k, v in asdict(self).items() if v is not None}
        # Paddings are authored in 96 DPI pixels; scale for the current display.
        for key in ("padx", "pady"):
            if key in options:
                options[key] = scale_pad(options[key])
        for key in ("ipadx", "ipady"):
            if key in options:
                options[key] = scale(options[key])
        return options
    
