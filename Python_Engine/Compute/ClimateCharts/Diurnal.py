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
from matplotlib.ticker import MaxNLocator

ANNUAL_DATETIME = pd.date_range(start="2018-01-01 00:30:00", freq="60T", periods=8760, closed="left")


def diurnal(annual_values: np.ndarray, save_path: str, grouping: str="Daily", months: np.ndarray=range(1, 13), title: str=None, unit: str=None, color: str="black", tone_color: str="black", transparency=False):
    """ Create a histogram with summary table for the data passed

    Parameters
    ----------
    annual_values : np.ndarray
        List of values to bin.
    save_path : str
        The full path where the plot will be saved.
    grouping : str
        The method of grouping the aggregate diurnal values. Choose from ["Daily", "Weekly", "Monthly"].
    months : np.ndarray
        A list of integers denoting the months to include in the summary
    title : str or None
        Adds a title to the plot.
    unit : str or None
        Adds a unit string to the y-axis of the plot.
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

    # Run input data checks
    assert len(annual_values) == 8760, \
        "Number of hourly values passed ({}) does not equal 8760".format(len(annual_values))

    assert ((min(months) >= 1) & (max(months) <= 12)), \
        "Month integers must be between 1 and 12 (inclusive)"

    # Convert passed values into a pd.Series object (and filter to remove unwanted months)
    series = pd.Series(annual_values, index=ANNUAL_DATETIME)[ANNUAL_DATETIME.month.isin(months)]

    if grouping == "Monthly":
        assert (len(months) == 12), \
            "Month filtering is not possible when grouping = \"Monthly\""

    assert os.path.exists(os.path.dirname(save_path)), \
        "\"{}\" does not exist".format(os.path.abspath(os.path.dirname(save_path)))

    # Define grouping methodologies
    groupings = {
        "Daily": {
            "grp": series.index.hour,
            "periods": 24,
            "xlabels": ["{0:02d}:00".format(i) for i in range(24)],
            "xticks": np.arange(0, 24, 1),
            "skip_n": [0, 1]
        },
        "Weekly": {
            "grp": [series.index.dayofweek, series.index.hour],
            "periods": 24 * 7,
            "xlabels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "xticks": np.arange(0, 24 * 7, 24),
            "skip_n": [0, 7]
        },
        "Monthly": {
            "grp": [series.index.month, series.index.hour],
            "periods": 24 * 12,
            "xlabels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            "xticks": np.arange(0, 24 * 12, 24),
            "skip_n": [0, 12]
        }
    }

    assert grouping in groupings.keys(), \
        "\"{}\" not available as a filter for grouping annual hourly data. Choose from {}".format(grouping, list(groupings.keys()))

    _grouping = series.groupby(groupings[grouping]["grp"])
    _min = _grouping.min().reset_index(drop=True)
    _mean = _grouping.mean().reset_index(drop=True)
    _max = _grouping.max().reset_index(drop=True)
    # TODO: Add end value to each day/week/month to fill gaps in Series

    # Instantiate plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 4))

    # Plot aggregate
    [ax.plot(_mean.iloc[i:i + 24], color=color, lw=2, label='Average') for i in np.arange(0, groupings[grouping]["periods"])[::24]]
    [ax.fill_between(np.arange(i, i + 24), _min.iloc[i:i + 24], _max.iloc[i:i + 24], color=color, alpha=0.2,
                     label='Range') for i in np.arange(0, groupings[grouping]["periods"])[::24]]
    ax.set_ylabel(unit, labelpad=2, color=tone_color)
    ax.yaxis.set_major_locator(MaxNLocator(7))

    # Format plot area
    [ax.spines[spine].set_visible(False) for spine in ['top', 'right']]
    [ax.spines[j].set_color(tone_color) for j in ['bottom', 'left']]
    ax.set_xlim([0, groupings[grouping]["periods"]])
    ax.xaxis.set_ticks(groupings[grouping]["xticks"])
    ax.set_xticklabels(groupings[grouping]["xlabels"], ha='left', color=tone_color)
    plt.setp(ax.get_yticklabels(), color=tone_color)
    ax.grid(b=True, which='major', axis='both', c=tone_color, ls='--', lw=1, alpha=0.3)
    ax.tick_params(length=0, labelleft=True, labelright=False, labeltop=False, labelbottom=True, color=tone_color)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(bbox_to_anchor=(0.5, -0.2), loc=8, ncol=3, borderaxespad=0., frameon=False,
                    handles=[handles[groupings[grouping]["skip_n"][0]], handles[groupings[grouping]["skip_n"][1]]], labels=[labels[groupings[grouping]["skip_n"][0]], labels[groupings[grouping]["skip_n"][1]]])
    lgd.get_frame().set_facecolor((1, 1, 1, 0))
    [plt.setp(text, color=tone_color) for text in lgd.get_texts()]

    # Add a title
    if title is None:
        plt_title = "{0:} diurnal profile".format(grouping)
    else:
        plt_title = "{0:}\n{1:} diurnal profile".format(title, grouping)
    title = plt.suptitle(plt_title, color=tone_color, ha="left", va="bottom", x=0, y=1.01, transform=ax.transAxes)

    # Tidy plot
    plt.tight_layout()

    # Save figure
    fig.savefig(save_path, bbox_inches="tight", dpi=300, transparent=False)

    return save_path
