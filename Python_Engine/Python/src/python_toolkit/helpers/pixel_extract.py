"""Methods to handle the extraction of pixel locations (based on colour) from images."""

# pylint: disable=C0302
# pylint: disable=E0401
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from python_toolkit.bhom.analytics import bhom_analytics
from scipy.spatial import KDTree
from tqdm import tqdm

from ..plot.utilities import average_color, similar_colors

# pylint: enable=E0401


@bhom_analytics()
def point_group(points: list[list[float]], threshold: float) -> list[list[float]]:
    """Cluster 2D points based on proximity.

    Args:
        points (list[list[float]]):
            A list of 2D points. This should be in the form [[x1, y1], [x2, y2], ...].
        threshold (float):
            The maximum distance between points to be considered neighbors.

    Returns:
        list[list[float]]:
            A list of points, each being average of the generated clusters.
    """

    class UnionFind:
        """Helper class implementing solution to point clustering from
        https://stackoverflow.com/a/77681823."""

        def __init__(self, n):
            self.parent = list(range(n))

        def find(self, i):
            """_"""
            if self.parent[i] != i:
                self.parent[i] = self.find(self.parent[i])
            return self.parent[i]

        def union(self, i, j):
            """_"""
            root_i = self.find(i)
            root_j = self.find(j)
            if root_i != root_j:
                self.parent[root_i] = root_j

    tree = KDTree(points)

    # Initialize Union-Find
    uf = UnionFind(len(points))

    # Find neighboring points within radius and union them
    for i, point in tqdm(list(enumerate(points)), desc="Clustering points ..."):
        neighbor_indices = tree.query_ball_point(point, threshold)
        for neighbor_index in neighbor_indices:
            uf.union(i, neighbor_index)

    # Collect fused points and assign labels
    label_groups = defaultdict(list)

    for i in range(len(points)):
        root = uf.find(i)
        label_groups[root].append(i)

    # create groups of points, and find the average (center) of each cluster
    clusters = []
    for _, points_indices in label_groups.items():
        grp = [points[i] for i in points_indices]
        clusters.append(np.mean(grp, axis=0).tolist())

    return clusters


@bhom_analytics()
def pixels_to_points(
    image_file: Path | str,
    color_keys: dict[str, list[str]],
    proximity_grouping: float,
    color_threshold: int = 5,
) -> Image:
    """Create a file containing pt-pixel location coordinates based on color keys.

    Args:
        image_file (Path | str):
            The path to the image file.
        color_keys (dict[str, list[str]]):
            A dictionary of color keys and their respective color values.
        proximity_grouping (float):
            The maximum distance between points to be considered neighbors.
        color_threshold (int, optional):
            The threshold for color matching. Defaults to 5.

    Notes:
        The color_keys dictionary should be in the following format:
        {
            "key1": ["#FFFFFF", "#000000"],
            "key2": ["#FF0000", "#00FF00"],
            ...
        }

    Returns:
        Image:
            An image with points representing the color keys.
    """

    # validation
    for k, v in color_keys.items():
        for vv in v:
            if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", vv):
                raise ValueError(f"{vv} is not a valid hex color")

    image_file = Path(image_file)

    # create a mapping in the form {(r, g, b): "key", }, including similar colors
    target_colors_hex = {}
    for k, v in color_keys.items():
        for hexcol in v:
            target_colors_hex[hexcol] = k
    target_colors_rgb = {}
    for k, v in target_colors_hex.items():
        for rgb in similar_colors(color=k, color_threshold=color_threshold, return_type="rgb_int"):
            target_colors_rgb[tuple(rgb)] = v

    # create average colour for each color group
    clrs = {}
    for k, v in color_keys.items():
        clrs[k] = average_color(colors=v, keep_alpha=False, return_type="hex")

    # load the image
    img = Image.open(image_file)
    pixels = img.load()
    width, height = img.size

    # iterate pixels, and find those where target_colors_rgb are present
    coords = {}
    for x in range(width):
        for y in range(height):
            try:
                k = target_colors_rgb[pixels[x, y][:-1]]
                if k not in coords:
                    coords[k] = [(x, y)]
                else:
                    coords[k].append((x, y))
            except KeyError:
                pass

    # cluster the points and group by proximity
    _temp = {}
    for k, points in coords.items():
        _temp[k] = [tuple(i) for i in point_group(points=points, threshold=proximity_grouping)]
    coords = _temp

    # convert coords into a more typical x, y, starting from bottom left of the image, cos that's easier to understand!
    normal_coords = {}
    for k, v in coords.items():
        normal_coords[k] = [(i, height - j) for i, j in v]

    # create new img with pts indicated
    new_im = img.copy().convert("LA").convert("RGB")
    draw = ImageDraw.Draw(new_im)
    s = 5
    for k, v in coords.items():
        for coord in v:
            draw.ellipse(
                (coord[0] - (s / 2), coord[1] - (s / 2), coord[0] + (s / 2), coord[1] + (s / 2)),
                outline="black",
                fill=clrs[k],
            )

    # write image to file in folder adjacent to original image
    _dir = image_file.absolute().parent / f"{image_file.stem}"
    _dir.mkdir(exist_ok=True, parents=True)
    new_im.save(_dir / f"{image_file.stem}.png")

    # write normalised coords to file in folder adjacent to original image
    for k, v in normal_coords.items():
        with open(_dir / f"{k}.dat", "w", encoding="utf-8") as fp:
            fp.write("\n".join([",".join([str(j) for j in i]) for i in v]))

    return new_im
