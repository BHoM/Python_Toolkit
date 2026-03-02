"""Typed packing options shared by BHoM Tkinter widgets."""

from dataclasses import dataclass, asdict
from typing import Any, Literal

from python_toolkit.bhom_tkinter.widgets._build_options import BuildOptions

@dataclass
class PackingOptions(BuildOptions):
    """Container for `pack` geometry keyword arguments with type hints."""

    after: Any = None
    anchor: Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se'] = 'center'
    before: Any = None
    expand: bool | Literal[0, 1] = 0
    fill: Literal['none', 'x', 'y', 'both'] = 'none'
    side: Literal['left', 'right', 'top', 'bottom'] = 'top'
    ipadx: float | str = 0.0
    ipady: float | str = 0.0
    padx: float | str | tuple[float | str, float | str] = 0.0
    pady: float | str | tuple[float | str, float | str] = 0.0
    in_: Any = None

    def to_dict(self) -> dict:
        """Convert the dataclass to a dictionary, excluding `None` values.

        Returns:
            dict: Packing options filtered to keys with concrete values.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}
                
if __name__ == "__main__":

    d = PackingOptions(side='left', fill='x', expand=True, padx=5, pady=5, anchor='w')
    print(d.to_dict())