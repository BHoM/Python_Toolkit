"""A named set of colours that can be registered with matplotlib as a colour map."""

from dataclasses import dataclass

from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap


@dataclass(frozen=True)
class Palette:
    """A named set of colours.

    Args:
        name: Name the palette is registered under in matplotlib.
        colours: Hex colours, in order.
        categorical: True if each colour is a separate category, False for a continuous gradient.
        colourblind_safe: True if the palette is distinguishable with the common colour vision deficiencies.
    """

    name: str
    colours: tuple[str, ...]
    categorical: bool = False
    colourblind_safe: bool = False

    def to_colormap(self) -> Colormap:
        """Build the matplotlib colour map for this palette.

        Returns:
            Colormap: A ListedColormap for a categorical palette, else a LinearSegmentedColormap.
        """
        if self.categorical:
            return ListedColormap(list(self.colours), name=self.name)
        return LinearSegmentedColormap.from_list(self.name, list(self.colours))
