import plotly.graph_objects as go
import pandas as pd
from matplotlib.colors import Colormap
import decimal as d

from ..bhom.analytics import bhom_analytics

def set_dimensions(df: pd.DataFrame, tick_mark_count: int, dp:int): -> list[dict[str, any]]

    """Set the dimensions for a parallel coordinate plot, based on column datatypes and unique values.
    
    Args:
        df (pd.DataFrame):
            The pandas DataFrame to plot.
        tick_mark_count (int):
            The number of tick marks to show on the parallel coordinate plot.
        dp (int):
            The number of decimal places to show on the tick marks.
                
    Returns:
        list[dict[str, any]]:
            A list of dimensions to plot.
    """
    
    df_copy = df.copy()
    dimensions = []

    for column in df_copy.columns:

        dim = {}
        dim['label'] = str(column)

        if df_copy[column].dtype == "object":
            #for catagorical data types, convert to numerical, with text as tick marks
            df_copy[column] = df_copy[column].astype("category").cat.codes

            dim['values'] = df_copy[column]
            dim['tickvals'] = df_copy[column].unique()
            dim['ticktext'] = df[column].unique()

            dimensions.append(dim)
            continue
        
        dim['values'] = df_copy[column]

        if df_copy[column].nunique() < tick_mark_count:

            dim['range'] = [df_copy[column].min(), df_copy[column].max()]
            dim['tickvals'] = dim['ticktext'] = df_copy[column].unique()

            dimensions.append(dim)

        else:
            # reduce the number of tick marks if the column has a large number of unique values
            dim['range'] = [df_copy[column].min(), df_copy[column].max()]
            dim['tickvals'] = [df_copy[column].min() + i * (df_copy[column].max() - df_copy[column].min()) / (tick_mark_count - 1) for i in range(tick_mark_count)]
            dim['ticktext'] = [round(i ,dp) for i in dim['tickvals']]

            dimensions.append(dim)

    return dimensions
        
@bhom_analytics()
def parallel_coordinate_plot(

    df: pd.DataFrame = pd.DataFrame(),
    variables_to_show: list = None,
    decimal_places: int = 0,
    tick_mark_count: int = 11,
    colour_key: str = None,
    cmap: Colormap = "viridis",
    dimensions: list[dict] = None,
    plot_title: str = "",
    plot_bgcolour: str = 'black',
    paper_bgcolour: str = 'black',
    font_colour: str = 'white',
    **kwargs,
) -> go.Figure:
    """Create a parallel coordinate plot of a pandas DataFrame.

    Args:
        df (pd.DataFrame):
            The pandas DataFrame to plot.
        variables_to_show (list, optional):
            The variables to show on the parallel coordinate plot. Must be a subset of df.columns.
        decimal_places (int, optional):
            The number of decimal places to show on the tick marks. Defaults to 0.
        tick_mark_count (int, optional):
            The number of tick marks to show on the parallel coordinate plot. Defaults to 11.
        colour_key (str, optional):
            The column to use as the colour key. Defaults to None.
        cmap (Colormap or str, optional):
            The colormap to use for the colour key. Can be a matplotlib Colormap or a string representing a Plotly colorscale. Defaults to "viridis".
        dimensions (list[dict], optional):
            A list of dimensions to plot. If None, dimensions will be automatically generated based on the DataFrame. Defaults to None.
        plot_title (str, optional):
            The title of the plot. Defaults to an empty string.
        plot_bgcolour (str, optional):
            The background color of the plot. Defaults to 'black'.
        paper_bgcolour (str, optional):
            The background color of the paper. Defaults to 'black'.
        font_colour (str, optional):
            The color of the font used in the plot. Defaults to 'white'.
        **kwargs:
            Additional keyword arguments to pass to go.Parcoords().
            
    Returns:
        go.Figure:
            The populated go.Figure object.
    """

    if variables_to_show is not None:
        df = df[variables_to_show]

    if dimensions is None:
        dimensions = set_dimensions(df, tick_mark_count, decimal_places)

    if colour_key is None and not df.empty:
        colour_key = df.columns[-1]
    
    line = dict(color=df[colour_key], colorscale=cmap)

    fig = go.Figure(
        data=go.Parcoords(
            line = line,
            dimensions = dimensions,
            **kwargs
        )
    )

    fig.update_layout(
        title = plot_title,
        plot_bgcolor = plot_bgcolour,
        paper_bgcolor = paper_bgcolour,
        font_color = font_colour
    )

    return fig