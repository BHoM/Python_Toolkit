"""Text and colour utility methods for plotting"""

import base64
import colorsys
import io
from pathlib import Path
from typing import Any, List
import copy

import pandas as pd

import numpy as np
from matplotlib.colors import (
    LinearSegmentedColormap,
    cnames,
    colorConverter,
    is_color_like,
    rgb2hex,
    to_hex,
    to_rgb,
    to_rgba_array,
)
import matplotlib.image as mimage
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.tri import Triangulation
from PIL import Image
from ..bhom.analytics import bhom_analytics

@bhom_analytics()
def average_color(colors: Any, keep_alpha: bool = False) -> str:
    """Return the average color from a list of colors.

    Args:
        colors (Any):
            A list of colors.
        keep_alpha (bool, optional):
            If True, the alpha value of the color is kept. Defaults to False.

    Returns:
        color: str
            The average color in hex format.
    """

    if not isinstance(colors, (list, tuple)):
        raise ValueError("colors must be a list")

    for i in colors:
        if not is_color_like(i):
            raise ValueError(
                f"colors must be a list of valid colors - '{i}' is not valid."
            )

    if len(colors) == 1:
        return colors[0]

    return rgb2hex(to_rgba_array(colors).mean(axis=0), keep_alpha=keep_alpha)

@bhom_analytics()
def animation(
    images: list[str | Path | Image.Image],
    output_gif: str | Path,
    ms_per_image: int = 333,
    transparency_idx: int = 0,
) -> Path:
    """Create an animated gif from a set of images.

    Args:
        images (list[str | Path | Image.Image]):
            A list of image files or PIL Image objects.
        output_gif (str | Path):
            The output gif file to be created.
        ms_per_image (int, optional):
            Number of milliseconds per image. Default is 333, for 3 images per second.
        transparency_idx (int, optional):
            The index of the color to be used as the transparent color. Default is 0.

    Returns:
        Path:
            The animated gif.

    """
    _images = []
    for i in images:
        if isinstance(i, (str, Path)):
            _images.append(Image.open(i))
        elif isinstance(i, Image.Image):
            _images.append(i)
        else:
            raise ValueError(
                f"images must be a list of strings, Paths or PIL Image objects - {i} is not valid."
            )

    # create white background
    background = Image.new("RGBA", _images[0].size, (255, 255, 255))

    _images = [Image.alpha_composite(background, i) for i in _images]

    _images[0].save(
        output_gif,
        save_all=True,
        append_images=_images[1:],
        optimize=False,
        duration=ms_per_image,
        loop=0,
        disposal=2,
        transparency=transparency_idx,
    )

    return output_gif

def create_title(text: str, plot_type: str) -> str:
    """Create a title for a plot.

    Args:
        text (str):
            The title of the plot.
        plot_type (str):
            The type of plot.

    Returns:
        str:
            The title of the plot.
    """
    return "\n".join(
        [
            i
            for i in [
                text,
                plot_type,
            ]
            if i is not None
        ]
    )

def contrasting_colour(color: Any):
    """Calculate the contrasting color for a given color.

    Args:
        color (Any):
            matplotlib color or sequence of matplotlib colors - Hex code,
            rgb-tuple, or html color name.

    Returns:
        str:
            String code of the contrasting color.
    """
    return ".15" if relative_luminance(color) > 0.408 else "w"

def relative_luminance(color: Any):
    """Calculate the relative luminance of a color according to W3C standards

    Args:
        color (Any):
            matplotlib color or sequence of matplotlib colors - Hex code,
            rgb-tuple, or html color name.

    Returns:
        float:
            Luminance value between 0 and 1.
    """
    rgb = colorConverter.to_rgba_array(color)[:, :3]
    rgb = np.where(rgb <= 0.03928, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lum = rgb.dot([0.2126, 0.7152, 0.0722])
    try:
        return lum.item()
    except ValueError:
        return lum

def colormap_sequential(
    *colors: str | float | int | tuple, N: int = 256
) -> LinearSegmentedColormap:
    """
    Create a sequential colormap from a list of input colors.

    Args:
        *colors (str | float | int | tuple):
            A list of colors according to their hex-code, string name, character code or
            RGBA values.
        N (int, optional):
            The number of colors in the colormap. Defaults to 256.

    Returns:
        LinearSegmentedColormap:
            A matplotlib colormap.

    Examples:
    >> colormap_sequential(
        (0.89411764705, 0.01176470588, 0.01176470588),
        "darkorange",
        "#FFED00",
        "#008026",
        (36/255, 64/255, 142/255),
        "#732982"
    )
    """

    if len(colors) < 2:
        raise KeyError("Not enough colors input to create a colormap.")

    fixed_colors = []
    for color in colors:
        fixed_colors.append(to_hex(color))

    return LinearSegmentedColormap.from_list(
        name=f"{'_'.join(fixed_colors)}",
        colors=fixed_colors,
        N=N,
    )

def annotate_imshow(
    im: mimage.AxesImage,
    data: list[float] = None,
    valfmt: str = "{x:.2f}",
    textcolors: tuple[str] = ("black", "white"),
    threshold: float = None,
    exclude_vals: list[float] = None,
    **text_kw,
) -> list[str]:
    """A function to annotate a heatmap.

    Args:
        im (AxesImage):
            The AxesImage to be labeled.
        data (list[float], optional):
            Data used to annotate. If None, the image's data is used. Defaults to None.
        valfmt (_type_, optional):
            The format of the annotations inside the heatmap. This should either use the string
            format method, e.g. "$ {x:.2f}", or be a `matplotlib.ticker.Formatter`.
            Defaults to "{x:.2f}".
        textcolors (tuple[str], optional):
            A pair of colors.  The first is used for values below a threshold, the second for
            those above.. Defaults to ("black", "white").
        threshold (float, optional):
            Value in data units according to which the colors from textcolors are applied. If None
            (the default) uses the middle of the colormap as separation. Defaults to None.
        exclude_vals (float, optional):
            A list of values where text should not be added. Defaults to None.
        **text_kw (dict, optional):
            All other keyword arguments are passed on to the created `~matplotlib.text.Text`

    Returns:
        list[str]:
            The texts added to the AxesImage.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max()) / 2.0

    # Set default alignment to center, but allow it to be overwritten by textkw.
    text_kw = {"ha": "center", "va": "center"}
    text_kw.update({"ha": "center", "va": "center"})

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = mticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] in exclude_vals:
                pass
            else:
                text_kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
                text = im.axes.text(j, i, valfmt(data[i, j], None), **text_kw)
                texts.append(text)

    return texts

def lighten_color(color: str | tuple, amount: float = 0.5) -> tuple[float]:
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.

    Args:
        color (str):
            A color-like string.
        amount (float):
            The amount of lightening to apply.

    Returns:
        tuple[float]:
            An RGB value.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    try:
        c = cnames[color]
    except KeyError:
        c = color
    c = colorsys.rgb_to_hls(*to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


@bhom_analytics()
def base64_to_image(base64_string: str, image_path: Path) -> Path:
    """Convert a base64 encoded image into a file on disk.

    Arguments:
        base64_string (str):
            A base64 string encoding of an image file.
        image_path (Path):
            The location where the image should be stored.

    Returns:
        Path:
            The path to the image file.
    """

    # remove html pre-amble, if necessary
    if base64_string.startswith("data:image"):
        base64_string = base64_string.split(";")[-1]

    with open(Path(image_path), "wb") as fp:
        fp.write(base64.decodebytes(base64_string.encode('utf-8')))

    return image_path

@bhom_analytics()
def image_to_base64(image_path: Path, html: bool = False) -> str:
    """Load an image file from disk and convert to base64 string.

    Arguments:
        image_path (Path):
            The file path for the image to be converted.
        html (bool, optional):
            Set to True to include the HTML preamble for a base64 encoded image. Default is False.

    Returns:
        str:
            A base64 string encoding of the input image file.
    """

    # convert path string to Path object
    image_path = Path(image_path).absolute()

    # ensure format is supported
    supported_formats = [".png", ".jpg", ".jpeg"]
    if image_path.suffix not in supported_formats:
        raise ValueError(
            f"'{image_path.suffix}' format not supported. Use one of {supported_formats}"
        )

    # load image and convert to base64 string
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")

    if html:
        content_type = f"data:image/{image_path.suffix.replace('.', '')}"
        content_encoding = "utf-8"
        return f"{content_type};charset={content_encoding};base64,{base64_string}"

    return base64_string

@bhom_analytics()
def figure_to_base64(figure: plt.Figure, html: bool = False, transparent: bool = True) -> str:
    """Convert a matplotlib figure object into a base64 string.

    Arguments:
        figure (Figure):
            A matplotlib figure object.
        html (bool, optional):
            Set to True to include the HTML preamble for a base64 encoded image. Default is False.

    Returns:
        str:
            A base64 string encoding of the input figure object.
    """

    buffer = io.BytesIO()
    figure.savefig(buffer, transparent=transparent)
    buffer.seek(0)
    base64_string = base64.b64encode(buffer.read()).decode("utf-8")

    if html:
        content_type = "data:image/png"
        content_encoding = "utf-8"
        return f"{content_type};charset={content_encoding};base64,{base64_string}"

    return base64_string

@bhom_analytics()
def figure_to_image(fig: plt.Figure) -> Image:
    """Convert a matplotlib Figure object into a PIL Image.

    Args:
        fig (Figure):
            A matplotlib Figure object.

    Returns:
        Image:
            A PIL Image.
    """

    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)
    buf = np.roll(buf, 3, axis=2)

    return Image.fromarray(buf)

@bhom_analytics()
def tile_images(
    imgs: list[Path] | list[Image.Image], rows: int, cols: int
) -> Image.Image:
    """Tile a set of images into a grid.

    Args:
        imgs (Union[list[Path], list[Image.Image]]):
            A list of images to tile.
        rows (int):
            The number of rows in the grid.
        cols (int):
            The number of columns in the grid.

    Returns:
        Image.Image:
            A PIL image of the tiled images.
    """

    imgs = np.array([Path(i) for i in np.array(imgs).flatten()])

    # open images if paths passed
    imgs = [Image.open(img) if isinstance(img, Path) else img for img in imgs]

    if len(imgs) != rows * cols:
        raise ValueError(
            f"The number of images given ({len(imgs)}) does not equal ({rows}*{cols})"
        )

    # ensure each image has the same dimensions
    w, h = imgs[0].size
    for img in imgs:
        if img.size != (w, h):
            raise ValueError("All images must have the same dimensions")

    w, h = imgs[0].size
    grid = Image.new("RGBA", size=(cols * w, rows * h))

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
        img.close()

    return grid

@bhom_analytics()
def triangulation_area(triang: Triangulation) -> float:
    """Calculate the area of a matplotlib Triangulation.

    Args:
        triang (Triangulation):
            A matplotlib Triangulation object.

    Returns:
        float:
            The area of the Triangulation in the units given.
    """

    triangles = triang.triangles
    x, y = triang.x, triang.y
    a, _ = triangles.shape
    i = np.arange(a)
    area = np.sum(
        np.abs(
            0.5
            * (
                (x[triangles[i, 1]] - x[triangles[i, 0]])
                * (y[triangles[i, 2]] - y[triangles[i, 0]])
                - (x[triangles[i, 2]] - x[triangles[i, 0]])
                * (y[triangles[i, 1]] - y[triangles[i, 0]])
            )
        )
    )

    return area

@bhom_analytics()
def create_triangulation(
    x: list[float],
    y: list[float],
    alpha: float = None,
    max_iterations: int = 250,
    increment: float = 0.01,
) -> Triangulation:
    """Create a matplotlib Triangulation from a list of x and y coordinates, including a mask to
        remove elements with edges larger than alpha.

    Args:
        x (list[float]):
            A list of x coordinates.
        y (list[float]):
            A list of y coordinates.
        alpha (float, optional):
            A value to start alpha at.
            Defaults to None, with an estimate made for a suitable starting point.
        max_iterations (int, optional):
            The number of iterations to run to check against triangulation validity.
            Defaults to 250.
        increment (int, optional):
            The value by which to increment alpha by when searching for a valid triangulation.
            Defaults to 0.01.

    Returns:
        Triangulation:
            A matplotlib Triangulation object.
    """

    if alpha is None:
        # TODO - add method here to automatically determine appropriate alpha value
        alpha = 1.1

    if len(x) != len(y):
        raise ValueError("x and y must be the same length")

    # Triangulate X, Y locations
    triang = Triangulation(x, y)

    xtri = x[triang.triangles] - np.roll(x[triang.triangles], 1, axis=1)
    ytri = y[triang.triangles] - np.roll(y[triang.triangles], 1, axis=1)
    maxi = np.max(np.sqrt(xtri**2 + ytri**2), axis=1)

    # Iterate triangulation masking until a possible mask is found
    count = 0
    fig, ax = plt.subplots(1, 1)
    synthetic_values = range(len(x))
    success = False
    while not success:
        count += 1
        try:
            tr = copy.deepcopy(triang)
            tr.set_mask(maxi > alpha)
            ax.tricontour(tr, synthetic_values)
            success = True
        except ValueError:
            alpha += increment
        else:
            break
        if count > max_iterations:
            plt.close(fig)
            raise ValueError(
                f"Could not create a valid triangulation mask within {max_iterations}"
            )
    plt.close(fig)
    triang.set_mask(maxi > alpha)
    return triang

@bhom_analytics()
def format_polar_plot(ax: plt.Axes, yticklabels: bool = True) -> plt.Axes:
    """Format a polar plot, to save on having to write this every time!"""
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # format plot area
    ax.spines["polar"].set_visible(False)
    ax.grid(True, which="both", ls="--", zorder=0, alpha=0.3)
    ax.yaxis.set_major_locator(plt.MaxNLocator(6))
    plt.setp(ax.get_yticklabels(), fontsize="small")
    ax.set_xticks(np.radians((0, 90, 180, 270)), minor=False)
    ax.set_xticklabels(("N", "E", "S", "W"), minor=False, **{"fontsize": "medium"})
    ax.set_xticks(
        np.radians(
            (22.5, 45, 67.5, 112.5, 135, 157.5, 202.5, 225, 247.5, 292.5, 315, 337.5)
        ),
        minor=True,
    )
    ax.set_xticklabels(
        (
            "NNE",
            "NE",
            "ENE",
            "ESE",
            "SE",
            "SSE",
            "SSW",
            "SW",
            "WSW",
            "WNW",
            "NW",
            "NNW",
        ),
        minor=True,
        **{"fontsize": "x-small"},
    )
    if not yticklabels:
        ax.set_yticklabels([])

def process_polar_data(data:pd.DataFrame, values_column:str, directions_column:str, directions:int=36, value_bins:List[float]=None):
    if value_bins is None:
        value_bins = np.linspace(min(data[values_column]), max(data[values_column]), 11)

    direction_bins = np.unique(
            ((np.linspace(0, 360, directions + 1) - ((360 / directions) / 2)) % 360).tolist()
            + [0, 360]
        )

    values_ser = data[values_column].copy()
    directions_ser = data[directions_column].copy()

    categories = pd.cut(values_ser, bins=value_bins, include_lowest=False)
    dir_categories = pd.cut(directions_ser, bins=direction_bins, include_lowest=True)
    bin_tuples = [tuple([i.left, i.right]) for i in categories.cat.categories.tolist()]
    dir_tuples = [tuple([i.left, i.right]) for i in dir_categories.cat.categories.tolist()][1:-1]
    dir_tuples.append((dir_tuples[-1][1], dir_tuples[0][0]))

    mapper = dict(
        zip(
            *[
                categories.cat.categories.tolist(),
                bin_tuples,
            ]
        )
    )
    mapper[np.nan] = bin_tuples[0]

    dir_mapper = dict(
        zip(
            *[
                dir_categories.cat.categories.tolist(),
                [dir_tuples[-1]] + dir_tuples,
            ]
        )
    )

    categories = pd.Series(
        [mapper[i] for i in categories],
        index=categories.index,
        name=categories.name,
    )

    dir_categories = pd.Series(
        [dir_mapper[i] for i in dir_categories],
        index=dir_categories.index,
        name=dir_categories.name,
    )

    df = pd.concat([dir_categories, categories], axis=1)

    #remove calm?

    # pivot dataframe
    df = (
        df.groupby([df.columns[0], df.columns[1]], observed=True)
        .value_counts()
        .unstack()
        .fillna(0)
        .astype(int)
    )

    for b in bin_tuples:
        if b not in df.columns:
            df[b] = 0
    df.sort_index(axis=1, inplace=True)
    df = df.T
    for b in dir_tuples:
        if b not in df.columns:
            df[b] = 0
    df.sort_index(axis=1, inplace=True)
    df = df.T

    df = df / df.values.sum() #as density plot

    return df
