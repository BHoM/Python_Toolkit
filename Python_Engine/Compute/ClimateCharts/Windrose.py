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
from matplotlib.cm import get_cmap
from windrose import WindroseAxes

ANNUAL_DATETIME = pd.date_range(start="2018-01-01 00:30:00", freq="60T", periods=8760, closed="left")

MASKS = {
    "Daily": ((ANNUAL_DATETIME.hour >= 0) & (ANNUAL_DATETIME.hour <= 24)),
    "Morning": ((ANNUAL_DATETIME.hour >= 5) & (ANNUAL_DATETIME.hour <= 10)),
    "Midday": ((ANNUAL_DATETIME.hour >= 11) & (ANNUAL_DATETIME.hour <= 13)),
    "Afternoon": ((ANNUAL_DATETIME.hour >= 14) & (ANNUAL_DATETIME.hour <= 18)),
    "Evening": ((ANNUAL_DATETIME.hour >= 19) & (ANNUAL_DATETIME.hour <= 22)),
    "Night": ((ANNUAL_DATETIME.hour >= 23) | (ANNUAL_DATETIME.hour <= 4)),
    "MorningShoulder": ((ANNUAL_DATETIME.hour >= 7) & (ANNUAL_DATETIME.hour <= 10)),
    "AfternoonShoulder": ((ANNUAL_DATETIME.hour >= 16) & (ANNUAL_DATETIME.hour <= 19)),

    "Annual": ((ANNUAL_DATETIME.month >= 1) & (ANNUAL_DATETIME.month <= 12)),
    "Spring": ((ANNUAL_DATETIME.month >= 3) & (ANNUAL_DATETIME.month <= 5)),
    "Summer": ((ANNUAL_DATETIME.month >= 6) & (ANNUAL_DATETIME.month <= 8)),
    "Autumn": ((ANNUAL_DATETIME.month >= 9) & (ANNUAL_DATETIME.month <= 11)),
    "Winter": ((ANNUAL_DATETIME.month <= 2) | (ANNUAL_DATETIME.month >= 12)),
    "Shoulder": ((ANNUAL_DATETIME.month == 3) | (ANNUAL_DATETIME.month == 10))
}


def windrose(
    annual_wind_speed: np.ndarray, 
    annual_wind_direction: np.ndarray, 
    save_path: str, 
    season_period: str="Annual", 
    time_period: str= "Daily", 
    n_sector: int=16, 
    title: str=None, 
    cmap: str= "GnBu", 
    tone_color: str= "black", 
    transparency: str=False
    ):
    """ Generates a windrose plot from a set of wind speeds and directions, with the ability to filter for specific time-periods.

    Parameters
    ----------
    annual_wind_speed : np.ndarray
        List of annual hourly wind speeds.
    annual_wind_direction : np.ndarray
        List of annual hourly wind directions.
    save_path : str
        The full path where the plot will be saved.
    season_period : str
        Choose from ["Annual", "Spring", "Summer", "Autumn", "Winter", "Shoulder"].
    time_period : str
        Choose from [Daily, "Morning", "Midday", "Afternoon", "Evening", "Night", "MorningShoulder", "AfternoonShoulder"].
    n_sector : int
        The number of directions to bin wind directions into.
    title : str or None
        Adds a title to the plot.
    cmap : str or None
        A Matplotlib valid colormap name. An up-to-date list of values is available from https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/colors.py.
    tone_color : str or None
        Text and border colours throughout the plot.
    transparency : bool
        Sets transparency of saved plot.

    Returns
    -------
    imagePath : str
        Path to the saved image
    """

    # Run checks on input data
    assert len(annual_wind_speed) == len(annual_wind_direction), \
        "Length of annual_wind_speed {} does not match length of annual_wind_direction {}".format(len(annual_wind_speed), len(annual_wind_direction))

    assert len(annual_wind_speed) == 8760, \
        "Number of hourly values passed ({}) does not equal 8760".format(len(annual_wind_speed))

    assert os.path.exists(os.path.dirname(save_path)), \
        "\"{}\" does not exist".format(os.path.abspath(os.path.dirname(save_path)))

    assert season_period in MASKS.keys(), \
        "\"{}\" not known as a filter for season periods. Choose from {}".format(season_period, list(MASKS.keys()))
    
    assert time_period in MASKS.keys(), \
        "\"{}\" not known as a filter for time periods. Choose from {}".format(time_period, list(MASKS.keys()))

    # Construct a DataFrame containing the annual wind speeds and directions
    df = pd.DataFrame(index=ANNUAL_DATETIME)
    df["wind_speed"] = annual_wind_speed
    df["wind_direction"] = annual_wind_direction

    # Create a set of masks to remove unwanted (null or zero) hours of the year, and for different time periods
    speed_mask = (df.wind_speed != 0)
    direction_mask = (df.wind_direction != 0)
    mask = np.array([MASKS[time_period], MASKS[season_period], speed_mask, direction_mask]).all(axis=0)

    # Weird bug fix here to create curved ends to polar bars
    plt.hist([0, 1]);
    plt.close()

    # Instantiate figure
    plt.figure(figsize=(6, 6))
    ax = WindroseAxes.from_ax()
    ax.bar(
        df.wind_direction[mask],
        df.wind_speed[mask],
        normed=True,
        bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        opening=0.95,
        edgecolor='White',
        lw=0.1,
        nsector=n_sector,
        cmap=get_cmap(cmap)
    )

    # Generate and format legend
    lgd = ax.legend(bbox_to_anchor=(1.1, 0.5), loc='center left', frameon=False, title="m/s")
    lgd.get_frame().set_facecolor((1, 1, 1, 0))
    [plt.setp(text, color=tone_color) for text in lgd.get_texts()]
    plt.setp(lgd.get_title(), color=tone_color)

    for i, leg in enumerate(lgd.get_texts()):
        b = leg.get_text().replace('[', '').replace(')', '').split(' : ')
        lgd.get_texts()[i].set_text(b[0] + ' to ' + b[1])

    # Format plot canvas
    ax.grid(linestyle=':', color=tone_color, alpha=0.5)
    ax.spines['polar'].set_visible(False)
    plt.setp(ax.get_xticklabels(), color=tone_color)
    plt.setp(ax.get_yticklabels(), color=tone_color)
    
    # Add title if provided
    if title is None:
        plt_title = "{0:} - {1:}".format(season_period, time_period)
    else:
        plt_title = "{0:} - {1:}\n{2:}".format(season_period, time_period, title)
    ax.set_title(plt_title, color=tone_color, ha="left", va="bottom", x=0, y=1.05, transform=ax.transAxes)

    # Save figure
    plt.savefig(save_path, bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=300, transparent=transparency)

    return save_path
