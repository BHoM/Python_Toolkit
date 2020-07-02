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


def frequency(values: np.ndarray, save_path: str, title: str=None, unit: str=None, vrange: np.ndarray=None, bins: int=10, color: str="black", tone_color: str="black", transparency=False):
    """ Create a histogram with summary table for the data passed

    Parameters
    ----------
    values : np.ndarray
        List of values to bin.
    save_path : str
        The full path where the plot will be saved.
    title : str or None
        Adds a title to the plot.
    unit : str or None
        Adds a unit string to the x-axis of the histogram.
    vrange : np.ndarray or None
        Sets the range of values within which the bins will be distributed.
    bins : int
        Number of bins into which the data should be sorted
    color : str
        A Matplotlib valid color name. An up-to-date list of values is available from https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/colors.py.
    tone_color : str or None
        Text and border colours throughout the plot.
    transparency : bool
        Sets transparency of saved plot.

    Returns
    -------
    imagePath : str
        Path to the saved image

    """

    assert os.path.exists(os.path.dirname(save_path)), \
        "\"{}\" does not exist".format(os.path.abspath(os.path.dirname(save_path)))

    # Convert passed values into a pd.Series object
    series = pd.Series(values)

    # Instantiate the plot and add sub-plots
    fig, ax = plt.subplots(1, 1, figsize=(15, 4))

    # Plot histogram
    if vrange is None:
        vrange = [series.min(), series.max()]
    ax.hist(series, bins=np.linspace(vrange[0], vrange[1], bins), color=color, alpha=0.9)

    # Format histogram
    ax.grid(b=True, which='major', color="k", linestyle=':', alpha=0.5, zorder=3)
    [ax.spines[spine].set_visible(False) for spine in ['top', 'right']]
    [ax.spines[j].set_color(tone_color) for j in ['bottom', 'left']]
    ax.tick_params(length=0, labelleft=True, labelright=False, labeltop=False, labelbottom=True, color=tone_color)
    ax.set_ylabel("Hours", color=tone_color)
    if vrange is None:
        ax.set_xlim(vrange)
    if unit is not None:
        ax.set_xlabel(unit, color=tone_color)
    plt.setp(ax.get_xticklabels(), ha='left', color=tone_color)
    plt.setp(ax.get_yticklabels(), color=tone_color)

    if title is not None:
        ax.set_title(title, color=tone_color, ha="left", va="bottom", x=0, y=1.01, transform=ax.transAxes)

    # Plot summary statistics
    _vals = np.round(series.describe().values, 2)
    _ids = ["Count", "Mean", "Std", "Min", "25%", "50%", "75%", "Max"]
    summary_text = ""
    max_id_length = max([len(i) for i in _ids])
    max_val_length = max([len(str(i)) for i in _vals])
    string_length = max_id_length + max_val_length
    for i, j in list(zip(*[_ids, _vals])):
        _id_length = len(i)
        _val_length = len(str(j))
        space_length = string_length - _id_length - _val_length
        summary_text += "{0:}: {1:}{2:}\n".format(i, " " * space_length, j)
    txt = ax.text(1.01, 1, summary_text, fontsize=12, color=tone_color, horizontalalignment='left', verticalalignment='top', transform=ax.transAxes, **{'fontname':'Courier New'})

    # Tidy plot
    plt.tight_layout()

    # Save figure
    fig.savefig(save_path, bbox_inches="tight", bbox_extra_artists=(txt,), dpi=300, transparent=transparency)

    return save_path
