
from typing import List
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PatchCollection
from matplotlib.colors import Colormap, ListedColormap, Normalize, to_hex
from matplotlib.patches import Rectangle
from pandas.tseries.frequencies import to_offset
import textwrap

def plot_polar(
        data: pd.DataFrame,
        value_column: str = "Value",
        direction_column: str = "Direction",
        ax: plt.Axes = None,
        directions: int = 36,
        value_bins: List[float] = None,
        colors: list[str | tuple[float] | Colormap] = None, #set of colours to use for the value bins
        title: str = None,
        legend: bool = True,
        ylim: tuple[float] = None,
        label: bool = False,
    ) -> plt.Axes:
        """Create a polar plot showing frequencies by direction.

        Args:
            data (pd.DataFrame):
                The data to plot. must be a dataframe with value and direction columns
            value_column (str, optional):
                The name of the column in the dataframe containing values.
                Defaults to 'Value'.
            direction_column (str):
                The name of the column in the dataframe containing directions.
                Defaults to 'Direction'.
            ax (plt.Axes, optional):
                The axes to plot this chart on. Defaults to None.
            directions (int, optional):
                The number of directions to use. Defaults to 36.
            value_bins (list[float]):
                The bins to use for the magnitudes of the values.
            colors: (str | tuple[float] | Colormap, optional):
                A list of colors to use for the value_bins. May also be a colormap.
            title (str, optional):
                title to display above the plot. Defaults to the source of this wind object.
            legend (bool, optional):
                Set to False to remove the legend. Defaults to True.
            ylim (tuple[float], optional):
                The y-axis limits. Defaults to None.
            label (bool, optional):
                Set to False to remove the bin labels. Defaults to False.

        Returns:
            plt.Axes: The axes object.
        """

        if ax is None:
            _, ax = plt.subplots(subplot_kw={"projection": "polar"})

        # create grouped data for plotting

        #TOM NOTE: need to find out exactly what this does. Likely it's just a dataframe pivot where each column is a values bin and the index is the direction bins (from the number of directions). Density seems to make values between 0-100%. remove_calm removes values below 0.1, though this should be implemented in an argument for this method instead.
        binned = self.histogram(
            directions=directions,
            other_data=other_data,
            other_bins=other_bins,
            density=True,
            remove_calm=True,
        )

        # set colors
        if colors is None:
            colors = [
                to_hex(plt.get_cmap("viridis")(i))
                for i in np.linspace(0, 1, len(binned.columns)) #TOM NOTE: number of bins
            ]
        if isinstance(colors, str):
            colors = plt.get_cmap(colors)
        if isinstance(colors, Colormap):
            colors = [to_hex(colors(i)) for i in np.linspace(0, 1, len(binned.columns))]
        if isinstance(colors, list | tuple):
            if len(colors) != len(binned.columns):
                raise ValueError(
                    f"colors must be a list of length {len(binned.columns)}, or a colormap."
                )

        #TOM NOTE: Don't change anything after this point

        # HACK to ensure that bar ends are curved when using a polar plot.
        fig = plt.figure()
        rect = [0.1, 0.1, 0.8, 0.8]
        hist_ax = plt.Axes(fig, rect)
        hist_ax.bar(np.array([1]), np.array([1]))

        if title is None or title == "":
            ax.set_title(textwrap.fill(f"{self.source}", 75))
        else:
            ax.set_title(title)

        theta_width = np.deg2rad(360 / directions)
        patches = []
        color_list = []
        x = theta_width / 2
        for _, data_values in binned.iterrows():
            y = 0
            for n, val in enumerate(data_values.values):
                patches.append(
                    Rectangle(
                        xy=(x, y),
                        width=theta_width,
                        height=val,
                        alpha=1,
                    )
                )
                color_list.append(colors[n])
                y += val
            if label:
                ax.text(x, y, f"{y:0.1%}", ha="center", va="center", fontsize="x-small")
            x += theta_width
        local_cmap = ListedColormap(np.array(color_list).flatten())
        pc = PatchCollection(patches, cmap=local_cmap)
        pc.set_array(np.arange(len(color_list)))
        ax.add_collection(pc)

        # construct legend
        if legend:
            handles = [
                mpatches.Patch(color=colors[n], label=f"{i} to {j}")
                for n, (i, j) in enumerate(binned.columns.values)
            ]
            _ = ax.legend(
                handles=handles,
                bbox_to_anchor=(1.1, 0.5),
                loc="center left",
                ncol=1,
                borderaxespad=0,
                frameon=False,
                fontsize="small",
                title=binned.columns.name,
                title_fontsize="small",
            )

        # set y-axis limits
        if ylim is None:
            ylim = (0, max(binned.sum(axis=1)))
        if len(ylim) != 2:
            raise ValueError("ylim must be a tuple of length 2.")
        ax.set_ylim(ylim)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))

        format_polar_plot(ax, yticklabels=True)

        return ax