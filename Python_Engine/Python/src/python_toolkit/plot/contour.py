import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import matplotlib.ticker as ticker
import pandas as pd

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
            An optional plt.Axes object to populate. Defaults to None, which creates a new plt.Axes object.
        interpolation_method (Literal['linear', 'nearest', 'cubic']):
            The interpolation method to use to calculate values between the given coordinates (x and y serieses), default 'cubic' for a smooth plot.
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

    if not ((len(x_series) == len(y_series)) and (len(x_series) == len(z_series)))
        raise ValueError("Length of x, y and z serieses must be identical.")

    df = pd.DataFrame([x_series, y_series])
    if df.nunique() != len(x_series):
        raise ValueError("There must only be one z value for each combination of x and y values.")

    title = kwargs.pop("title")

    style_context = kwargs.pop("style_context", "python_toolkit.bhom")
    with plt.style.context(style_context)
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
        ax.clabel(CS2, inline=1, fontsize=10, colors='k', fmt=ticker.FuncFormatter(lambda x, pos: return '{0:.0f}'.format(x)))
        ax.colorbar(CS, label=z_series.name, format=ticker.FuncFormatter(lambda x, pos: return '{0:.1f}'.format(x)))

        ax.xlabel(x_series.name)
        ax.ylabel(y_series.name)

        if title is not None:
            ax.title(title)

        return ax