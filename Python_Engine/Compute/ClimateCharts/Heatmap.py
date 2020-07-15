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
from matplotlib.dates import date2num, DateFormatter

ANNUAL_DATETIME = pd.date_range(start="2018-01-01 00:30:00", freq="60T", periods=8760, closed="left")


def heatmap(
    annual_values: np.ndarray, 
    save_path: str, 
    title: str = None, 
    unit: str = None,
    vrange: np.ndarray = None, 
    cmap: str = 'viridis', 
    tone_color: str = "black", 
    invert_y: bool = False,
    transparency: bool = False
    ):
    """ Generate a heatmap from a set of annual hourly values

    Parameters
    ----------
    annual_values : np.ndarray
        List of 8760 annual hourly values.
    save_path : str
        The full path where the plot will be saved.
    title : str or None
        Adds a title to the plot.
    unit : str or None
        Adds a unit string to the color-bar associated with the heatmap.
    vrange : np.ndarray or None
        Sets the range of values within which the color-bar will be applied.
    cmap : str or None
        A Matplotlib valid colormap name. An up-to-date list of values is available from https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/_color_data.py.
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

    # Reshape data into time/day matrix
    annual_matrix = df.pivot_table(columns=df.index.date, index=df.index.time).values[::-1]

    # Instantiate figure
    fig, ax = plt.subplots(1, 1, figsize=(15, 5))

    # Plot data
    heatmap = ax.imshow(
        annual_matrix,
        extent=[date2num(df.index.min()), date2num(df.index.max()), 726449, 726450],
        aspect='auto',
        cmap=cmap,
        interpolation='none',
        vmin=vrange[0] if vrange is not None else None,
        vmax=vrange[-1] if vrange is not None else None,
    )

    # Axis formatting
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.yaxis_date()
    ax.yaxis.set_major_formatter(DateFormatter('%H:%M'))
    if invert_y:
        ax.invert_yaxis()
    ax.tick_params(labelleft=True, labelright=True, labelbottom=True, color=tone_color)
    plt.setp(ax.get_xticklabels(), ha='left', color=tone_color)
    plt.setp(ax.get_yticklabels(), color=tone_color)

    # Spine formatting
    [ax.spines[spine].set_visible(False) for spine in ['top', 'bottom', 'left', 'right']]

    # Grid formatting
    ax.grid(b=True, which='major', color='white', linestyle=':', alpha=1)

    # Color-bar formatting
    cb = fig.colorbar(heatmap, orientation='horizontal', drawedges=False, fraction=0.05, aspect=100, pad=0.075)
    plt.setp(plt.getp(cb.ax.axes, 'xticklabels'), color=tone_color)
    cb.set_label(unit, color=tone_color)
    cb.outline.set_visible(False)

    # Add title if provided
    if title is not None:
        plt.title(title, color=tone_color, ha="left", va="bottom", x=0, y=1.01, transform=ax.transAxes)

    # Tidy plot
    plt.tight_layout()

    # Save figure
    fig.savefig(save_path, bbox_inches="tight", dpi=300, transparent=transparency)

    return save_path
