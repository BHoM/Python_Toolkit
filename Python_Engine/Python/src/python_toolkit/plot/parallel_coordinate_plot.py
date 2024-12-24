import plotly.graph_objects as go
import pandas as pd
from matplotlib.colors import Colormap
import decimal as d

#from ..bhom.analytics import bhom_analytics

def set_dimensions(df, tick_mark_count, dp):
    
    df_copy = df.copy()
    dimensions = []

    for column in df_copy.columns:

        dim = {}
        dim['label'] = str(column)

        if df_copy[column].dtype == "object":
            print('column is object', column)
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

            # not quantiles, equally spaced marks

            dimensions.append(dim)

    #need to add the text back to catagorical data types
    return dimensions
        
#@bhom_analytics()
def parallel_coordinate_plot(

    df: pd.DataFrame,
    variables_to_show: list = None,
    decimal_places: int = 0,
    tick_mark_count: int = 11,
    colour_key: str = None,
    cmap: Colormap = "viridis",
    dimensions: list[dict] = None,
    plot_title: str = "",
    plot_bgcolor: str = 'black',
    paper_bgcolor: str = 'black',
    font_color: str = 'white',
    **kwargs,
) -> go.Figure:
    """Create a parallel coordinate plot of a pandas DataFrame.

    Args:
        df (pd.DataFrame):
            The pandas DataFrame to plot.
        variables_to_show (list, optional):
            The variables to show on the parallel coordinate plot. must be a subset of df.columns.
        decimal_places (int, optional):
            The number of decimal places to show on the tick marks. Defaults to 0.
        tick_mark_count (int, optional):
            The number of tick marks to show on the parallel coordinate plot. Defaults to 10.
        colour_key (str, optional):
            The column to use as the colour key. Defaults to None.
        cmap (Colormap, optional):
            The colormap to use for the colour key. Defaults to "viridis".
        dimensions (list[dict], optional):
            A list of dimensions to plot. Defaults to None.
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

    if colour_key is not None:
        line = dict(color=df[colour_key],
                     colorscale=cmap)
    else:
        line = dict()

    fig = go.Figure(
        data=go.Parcoords(
            line = line,
            dimensions = dimensions,
            **kwargs
        )
    )

    fig.update_layout(
        title = plot_title,
        plot_bgcolor = plot_bgcolor,
        paper_bgcolor = paper_bgcolor,
        font_color = font_color
    )

    return fig