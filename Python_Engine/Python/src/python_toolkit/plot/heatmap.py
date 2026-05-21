"""Methods for plotting heatmaps from time-indexed data."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Literal
from scipy.interpolate import griddata
import matplotlib.ticker as ticker
from ..bhom.analytics import bhom_analytics
from ..helpers.timeseries import validate_timeseries


@bhom_analytics()
def heatmap(
    series: pd.Series,
    ax: plt.Axes = None,
    **kwargs,
) -> plt.Axes:
    """Create a heatmap of a pandas Series.

    Args:
        series (pd.Series):
            The pandas Series to plot. Must have a datetime index.
        ax (plt.Axes, optional):
            An optional plt.Axes object to populate. Defaults to None, which creates a new plt.Axes object.
        **kwargs:
            Additional keyword arguments to pass to plt.pcolormesh().
            show_colorbar (bool, optional):
                If True, show the colorbar. Defaults to True.
            title (str, optional):
                The title of the plot. Defaults to None.
            mask (List[bool], optional):
                A list of booleans to mask the data. Defaults to None.
            style_context (string, optional):
                The matplotlib style to use. Defaults to python_toolkit.bhom
    Returns:
        plt.Axes:
            The populated plt.Axes object.
    """
    validate_timeseries(series)
    
    day_time_matrix = (
        series.dropna()
        .to_frame()
        .pivot_table(columns=series.dropna().index.date, index=series.dropna().index.time)
    )
    x = mdates.date2num(day_time_matrix.columns.get_level_values(1))
    y = mdates.date2num(
        pd.to_datetime([f"2017-01-01 {i}" for i in day_time_matrix.index])
    )
    z = day_time_matrix.values

    if "mask" in kwargs:
        if not isinstance(kwargs["mask"], (list, np.ndarray, pd.Series)):
            raise TypeError("The type of 'mask' must be a list, numpy ndarray or pandas Series")
        if len(kwargs["mask"]) != len(series):
            raise ValueError(
                f"Length of mask ({len(kwargs['mask'])}) must match length of data ({len(series)})."
            )
        mask_flip = pd.Series(kwargs.pop("mask")).to_frame().pivot_table(columns=series.index.date, index=series.index.time)
        z = np.ma.masked_array(z, mask=mask_flip)

    # handle non-standard kwargs
    extend = kwargs.pop("extend", "neither")
    title = kwargs.pop("title", series.name)
    show_colorbar = kwargs.pop("show_colorbar", True)
    style_context = kwargs.pop("style_context", "python_toolkit.bhom")

    with plt.style.context(style_context):
        # Plot data
        if ax is None:
            ax = plt.gca()

        pcm = ax.pcolormesh(
            x,
            y,
            z[:-1, :-1],
            **kwargs,
        )

        ax.xaxis_date()
        if len(set(series.index.year)) > 1:
            date_formatter = mdates.DateFormatter("%b %Y")
        else:
            date_formatter = mdates.DateFormatter("%b")
        ax.xaxis.set_major_formatter(date_formatter)

        ax.yaxis_date()
        ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        ax.tick_params(labelleft=True, labelbottom=True)
        plt.setp(ax.get_xticklabels(), ha="left")

        for spine in ["top", "bottom", "left", "right"]:
            ax.spines[spine].set_visible(False)

        for i in ax.get_xticks():
            ax.axvline(i, color="w", ls=":", lw=0.5, alpha=0.5)

        for i in ax.get_yticks():
            ax.axhline(i, color="w", ls=":", lw=0.5, alpha=0.5)

        if show_colorbar:
            cb = plt.colorbar(
                pcm,
                ax=ax,
                orientation="horizontal",
                drawedges=False,
                fraction=0.05,
                aspect=100,
                pad=0.075,
                extend=extend,
                label=series.name,
            )
            cb.outline.set_visible(False)

        ax.set_title(title)

    return ax

def contour(
    x_series: pd.Series,
    y_series: pd.Series,
    z_series: pd.Series,
    ax: plt.Axes = None,
    interpolation_method: Literal['linear', 'nearest', 'cubic'] = 'cubic',
    **kwargs
    ) -> plt.Axes:
    """
    Create a contour plot using 3 pandas serieses.

    Args:
        x_series (pd.Series):
            The pandas Series with x coordinates to plot with.
        y_series (pd.Series):
            The pandas Series with y coordinates to plot with.
        z_series (pd.Series):
            The pandas Series to plot z values (colours).
        ax (plt.Axes, optional):
            An optional plt.Axes object to populate. Defaults to None, which uses the currently loaded axes (or creates a new one if it doesn't exist).
        interpolation_method (Literal['linear', 'nearest', 'cubic']):
            The interpolation method to use to calculate values between the given coordinates (x and y serieses), default 'cubic' for a smooth plot.
        **kwargs:
            Additional keyword arguments to pass to ax.contourf().
            show_colorbar (bool, optional):
                If True, show the colorbar. Defaults to True.
            title (str, optional):
                The title of the plot. Defaults to None.
            mask (List[bool], optional):
                A list of booleans to mask the data. Defaults to None.
            style_context (string, optional):
                The matplotlib style to use. Defaults to python_toolkit.bhom
    Returns:
        plt.Axes:
            The populated plt.Axes object.
    """

    if not ((len(x_series) == len(y_series)) and (len(x_series) == len(z_series))):
        raise ValueError("Length of x, y and z serieses must be identical.")

    df = pd.DataFrame([x_series, y_series])
    if df.duplicated().any():
        raise ValueError("There must only be one z value for each combination of x and y values.")
        
    extend = kwargs.pop("extend", "neither")
    title = kwargs.pop("title", z_series.name)
    show_colorbar = kwargs.pop("show_colorbar", True)

    style_context = kwargs.pop("style_context", "python_toolkit.bhom")
    with plt.style.context(style_context):
        if ax is None:
            ax = plt.gca()

        # Convert data from pandas dataframes to numpy arrays
        X0, Y0, Z0, = np.array([]), np.array([]), np.array([])
        for i in range(len(x_series)):
            X0 = np.append(X0, x_series[i])
            Y0 = np.append(Y0, y_series[i])
            Z0 = np.append(Z0, z_series[i])

        # Create x-y points to be used in heatmap (allows smoother transitions for cubic interpolation method)
        xi = np.linspace(X0.min(), X0.max(), 1000)
        yi = np.linspace(Y0.min(), Y0.max(), 1000)

        # Plot using requested interpolation method
        zi = griddata((X0, Y0), Z0, (xi[None,:], yi[:,None]), method=interpolation_method)

        # Create the contour plot
        CS = ax.contourf(xi, yi, zi, 150, vmax=zi.max(), vmin=zi.min(), **kwargs)

        # Add the contour lines
        intervals = int(zi.max() - zi.min())
        CS2 = ax.contour(xi, yi, zi, intervals, colors='k')

        # Format contour and colourbar labels.
        ax.clabel(CS2, inline=1, fontsize=10, colors='k', fmt=ticker.FuncFormatter(lambda x, pos: '{0:.0f}'.format(x)))
        
        if show_colorbar:
            cb = plt.colorbar(
                CS,
                ax=ax,
                orientation="horizontal",
                drawedges=False,
                fraction=0.05,
                aspect=100,
                pad=0.175,
                extend=extend,
                label=z_series.name,
                format=ticker.FuncFormatter(lambda x, pos: '{0:.1f}'.format(x))
            )
            cb.outline.set_visible(False)

        ax.set_xlabel(x_series.name)
        ax.set_ylabel(y_series.name)
        ax.set_title(title)

        return ax