from matplotlib import pyplot as plt
from matplotlib.colors import Colormap, Normalize
from matplotlib.figure import Figure
import numpy as np
from typing import Union, Optional

plt.rcParams["figure.max_open_warning"] = 0

def cmap_sample_plot(
    cmap: Union[str, Colormap],
    bounds: Optional[tuple] = None,
    figsize: tuple = (9, 1),
    bins: int = 256
) -> Figure:

    """
    Generate a sample plot for a given colormap.
    
    Args:
        cmap: Either a colormap string (e.g., 'viridis') or a custom Colormap object
        bounds: Optional tuple of (vmin, vmax) for normalization. If None, uses (0, 1)
        figsize: Figure size as (width, height)
        bins: Number of discrete bins for the gradient. Defaults to 256.
    Returns:
        Matplotlib Figure object
    """

    # Set bounds
    if bounds is None:
        bounds = (0, 1)
    
    vmin, vmax = bounds
    
    # Create a gradient image with appropriate range.
    # Use endpoint=False to avoid an emphasized terminal color column at the
    # right edge when rasterized into a small preview.
    gradient_row = np.linspace(vmin, vmax, bins, endpoint=False)
    gradient = np.vstack([gradient_row, gradient_row])
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0)
    fig.patch.set_facecolor("none")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.set_position([0, 0, 1, 1])
    ax.margins(x=0, y=0)
    
    # Create normalization if custom colormap or custom bounds
    norm = Normalize(vmin=vmin, vmax=vmax)
    
    # Display the gradient with the specified colormap
    ax.imshow(
        gradient,
        aspect="auto",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
        resample=False,
    )
    
    # Remove axes for a cleaner look
    ax.set_axis_off()
    
    return fig

if __name__ == "__main__":
    # Example 1: Using a preset colormap string
    fig1 = cmap_sample_plot('viridis')
    
    # Example 2: Using a custom colormap with bounds
    fig2 = cmap_sample_plot('plasma', bounds=(0, 100), bins=6)
    
    # Example 3: Creating and using a custom colormap
    from matplotlib.colors import ListedColormap
    custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    custom_cmap = ListedColormap(custom_colors)
    fig3 = cmap_sample_plot(custom_cmap, bounds=(0, 3))
    
    plt.show()