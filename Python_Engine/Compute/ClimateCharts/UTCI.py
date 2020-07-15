#
# This file is part of the Buildings and Habitats object Model (BHoM)
# Copyright (c) 2015 - 2020, the respective contributors. All rights reserved.
#
# Each contributor holds copyright over their respective contributions.
# The project versioning (Git) records all such contribution source information.
#
#
# The BHoM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3.0 of the License, or
# (at your option) any later version.
#
# The BHoM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this code. If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.
#

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.dates import date2num, DateFormatter

ANNUAL_DATETIME = pd.date_range(start="2018-01-01 00:30:00", freq="60T", periods=8760, closed="left")


def utci(
    annual_values: np.ndarray, 
    save_path: str, 
    detailed: bool = False, 
    title: str = None, 
    tone_color: str = "black", 
    invert_y: bool = False,
    transparency: bool = False
    ):
    """ Generate a UTCI heatmap from a set of annual hourly values

    Parameters
    ----------
    annual_values : np.ndarray
        List of 8760 annual hourly values.
    save_path : str
        The full path where the plot will be saved.
    detailed : bool
        Set to True to include monthly stacked charts with proportion of time comfortable.
    title : str or None
        Adds a title to the plot.
    tone_color : str or None
        Text and border colours throughout the plot.
    invert_y : bool
        Reverse the y-axis so that 0-24 hours runs from top to bottom.
    transparency : bool
        Sets transparency of saved plot.

    Returns
    -------
    imagePath : str
        Path to the saved image
    """

    # Run input data checks
    assert len(annual_values) == 8760, \
        "Number of hourly values passed ({}) does not equal 8760".format(len(annual_values))

    assert os.path.exists(os.path.dirname(save_path)), \
        "\"{}\" does not exist".format(os.path.abspath(os.path.dirname(save_path)))

    # Create DataFrame from passed values
    df = pd.DataFrame(data=annual_values, index=ANNUAL_DATETIME, columns=[title])

    # Reshape data into time/day matrix for heatmap plotting
    annual_matrix = df.pivot_table(columns=df.index.date, index=df.index.time).values[::-1]

    # Create UTCI colormap
    utci_cmap = ListedColormap(['#0D104B', '#262972', '#3452A4', '#3C65AF', '#37BCED', '#2EB349', '#F38322', '#C31F25', '#7F1416', '#580002'])
    utci_cmap_bounds = [-100, -40, -27, -13, 0, 9, 26, 32, 38, 46, 100]
    utci_cmap_norm = BoundaryNorm(utci_cmap_bounds, utci_cmap.N)

    bounds = np.arange(-41, 48, 1)
    norm = BoundaryNorm(bounds, utci_cmap.N)

    if not detailed:
        # Instantiate figure
        fig, ax = plt.subplots(1, 1, figsize=(15, 5))

        # Plot data
        heatmap = ax.imshow(
            annual_matrix,
            extent=[date2num(df.index.min()), date2num(df.index.max()), 726449, 726450],
            aspect='auto',
            cmap=utci_cmap,
            interpolation='none',
            vmin=-40,
            vmax=46,
            norm=utci_cmap_norm
        )

        # Axis formatting
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.yaxis_date()
        ax.yaxis.set_major_formatter(DateFormatter('%H:%M'))
        if invert_y:
            ax.invert_yaxis()
        ax.tick_params(length=0, labelleft=True, labelright=True, labeltop=False, labelbottom=True, color=tone_color)
        plt.setp(ax.get_xticklabels(), ha='left', color=tone_color)
        plt.setp(ax.get_yticklabels(), color=tone_color)

        # Spine formatting
        [ax.spines[spine].set_visible(False) for spine in ['top', 'bottom', 'left', 'right']]

        # Grid formatting
        ax.grid(b=True, which='major', color='white', linestyle=':', alpha=1)

        # Add colorbar legend and text descriptors for comfort bands
        # cb = fig.colorbar(heatmap, orientation='horizontal', drawedges=False, fraction=0.05, aspect=100, pad=0.075)
        cb = fig.colorbar(heatmap, cmap=utci_cmap, norm=norm, boundaries=bounds, orientation='horizontal', drawedges=False, fraction=0.05, aspect=100, pad=0.15, extend='both', ticks=[-40, -27, -13, 0, 9, 26, 32, 38, 46])
        plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color=tone_color)
        cb.set_label("°C", color=tone_color)
        cb.outline.set_visible(False)
        y_move = -0.135
        ax.text(0, y_move, 'Extreme\ncold stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(-27 + (-40 - -27) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Very strong\ncold stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(-13 + (-27 - -13) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Strong\ncold stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(0 + (-13 - 0) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Moderate\ncold stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(0 + (9 - 0) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Slight\ncold stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(9 + (26 - 9) / 2, [-44.319, 50.319], [0, 1]), y_move, 'No thermal stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(26 + (32 - 26) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Moderate\nheat stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(32 + (38 - 32) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Strong\nheat stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(np.interp(38 + (46 - 38) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Very strong\nheat stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')
        ax.text(1, y_move, 'Extreme\nheat stress', ha='center', va='center', transform=ax.transAxes, color=tone_color, fontsize='small')

        # Add title if provided
        if title is None:
            plt_title = "Universal Thermal Climate Index"
        else:
            plt_title = "{0:}\nUniversal Thermal Climate Index".format(title)
        ti = plt.title(plt_title, color=tone_color, ha="left", va="bottom", x=0, y=1.01, transform=ax.transAxes)

    else:
        fig = plt.figure(figsize=(15, 6), constrained_layout=True)
        spec = fig.add_gridspec(ncols=1, nrows=2, width_ratios=[1], height_ratios=[2, 1], hspace=0.1)

        hmap = fig.add_subplot(spec[0, 0])
        hbar = fig.add_subplot(spec[1, 0])

        # Plot heatmap
        heatmap = hmap.imshow(pd.pivot_table(df, index=df.index.time, columns=df.index.date,
                                             values=df.columns[0]).values[::-1], norm=utci_cmap_norm,
                              extent=[date2num(df.index.min()), date2num(df.index.max()), 726449,
                                      726450],
                              aspect='auto', cmap=utci_cmap, interpolation='none', vmin=-40, vmax=46)
        hmap.xaxis_date()
        hmap.xaxis.set_major_formatter(DateFormatter('%b'))
        hmap.yaxis_date()
        hmap.yaxis.set_major_formatter(DateFormatter('%H:%M'))
        if invert_y:
            hmap.invert_yaxis()
        hmap.tick_params(length=0, labelleft=True, labelright=True, labeltop=False, labelbottom=True, color=tone_color)
        plt.setp(hmap.get_xticklabels(), ha='left', color=tone_color)
        plt.setp(hmap.get_yticklabels(), color=tone_color)
        for spine in ['top', 'bottom', 'left', 'right']:
            hmap.spines[spine].set_visible(False)
            hmap.spines[spine].set_color(tone_color)
        hmap.grid(b=True, which='major', color="white", linestyle=':', alpha=1)

        # Add colorbar legend and text descriptors for comfort bands
        cb = fig.colorbar(heatmap, cmap=utci_cmap, norm=norm, boundaries=bounds,
                          orientation='horizontal', drawedges=False, fraction=0.01, aspect=50,
                          pad=-0.0, extend='both', ticks=[-40, -27, -13, 0, 9, 26, 32, 38, 46])
        plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color=tone_color)
        cb.outline.set_visible(False)
        cb.set_label("°C", color=tone_color)

        y_move = -0.4
        hbar.text(0, y_move, 'Extreme\ncold stress', ha='center', va='center', transform=hbar.transAxes,
                  color=tone_color,
                  fontsize='small')
        hbar.text(np.interp(-27 + (-40 - -27) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Very strong\ncold stress',
                  ha='center', va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(-13 + (-27 - -13) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Strong\ncold stress',
                  ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(0 + (-13 - 0) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Moderate\ncold stress', ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(0 + (9 - 0) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Slight\ncold stress', ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(9 + (26 - 9) / 2, [-44.319, 50.319], [0, 1]), y_move, 'No thermal stress', ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(26 + (32 - 26) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Moderate\nheat stress',
                  ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(32 + (38 - 32) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Strong\nheat stress', ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(np.interp(38 + (46 - 38) / 2, [-44.319, 50.319], [0, 1]), y_move, 'Very strong\nheat stress',
                  ha='center',
                  va='center', transform=hbar.transAxes, color=tone_color, fontsize='small')
        hbar.text(1, y_move, 'Extreme\nheat stress', ha='center', va='center', transform=hbar.transAxes,
                  color=tone_color,
                  fontsize='small')

        # Add stacked plot
        bins = [-100, -40, -27, -13, 0, 9, 26, 32, 38, 46, 100]
        tags = ["Extreme cold stress", "Very strong cold stress", "Strong cold stress", "Moderate cold stress",
                "Slight cold stress", "No thermal stress", "Moderate heat stress", "Strong heat stress",
                "Very strong heat stress", "Extreme heat stress"]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        clrs = utci_cmap.colors

        adf = pd.DataFrame()
        for mnth_n, mnth in enumerate(months):
            # Filter the series to return only the month
            a = df[df.index.month == mnth_n + 1].dropna().values
            a = pd.Series(index=tags, name=mnth,
                          data=[((a > i) & (a <= j)).sum() / len(a) for n, (i, j) in
                                enumerate(zip(bins[:-1], bins[1:]))])
            adf = pd.concat([adf, a], axis=1)
        adf = adf.T[tags]
        adf.plot(kind="bar", ax=hbar, stacked=True, color=clrs, width=1, legend=False)
        hbar.set_xlim(-0.5, 11.5)
        #
        # # Major ticks
        hbar.set_xticks(np.arange(-0.5, 11, 1))

        # Labels for major ticks
        hbar.set_xticklabels(months)

        plt.setp(hbar.get_xticklabels(), ha='center', rotation=0, color=tone_color)
        plt.setp(hbar.get_xticklabels(), ha='left', color=tone_color)
        plt.setp(hbar.get_yticklabels(), color=tone_color)
        for spine in ['top', 'right']:
            hbar.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            hbar.spines[spine].set_color(tone_color)
        hbar.grid(b=True, which='major', color="white", linestyle=':', alpha=1)
        hbar.set_yticklabels(['{:,.0%}'.format(x) for x in hbar.get_yticks()])

        # Add header percentages for bar plot
        cold_percentages = adf.iloc[:, :5].sum(axis=1).values
        comfortable_percentages = adf.iloc[:, 5]
        hot_percentages = adf.iloc[:, 6:].sum(axis=1).values
        for n, (i, j, k) in enumerate(zip(*[cold_percentages, comfortable_percentages, hot_percentages])):
            hbar.text(n, 1.02, "{0:0.1f}%".format(i * 100), va="bottom", ha="center", color="#3C65AF", fontsize="small")
            hbar.text(n, 1.02, "{0:0.1f}%\n".format(j * 100), va="bottom", ha="center", color="#2EB349",
                      fontsize="small")
            hbar.text(n, 1.02, "{0:0.1f}%\n\n".format(k * 100), va="bottom", ha="center", color="#C31F25",
                      fontsize="small")
        hbar.set_ylim(0, 1)

        # Add title if provided
        if title is None:
            plt_title = "Universal Thermal Climate Index"
        else:
            plt_title = "{0:}\nUniversal Thermal Climate Index".format(title)
            ti = hmap.set_title(plt_title, color=tone_color, ha="left", va="bottom", x=0, y=1.01, transform=hmap.transAxes)

    # Tidy figure
    plt.tight_layout()

    # Save figure
    fig.savefig(save_path, bbox_inches="tight", bbox_extra_artists=[ti,], dpi=300, transparent=transparency)

    return save_path
