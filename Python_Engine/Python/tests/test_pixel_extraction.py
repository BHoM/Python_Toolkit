"""Test methods for pixel_extract.py"""

from python_toolkit.helpers.nuke_directory import nuke_directory
from python_toolkit.helpers.pixel_extract import Image, pixels_to_points

from . import EXAMPLE_IMAGE


def test_pixels_to_points():
    """_"""

    # run method
    color_keys = {
        "Gold": ["#ffc90e"],
        "Green": ["#22b14c", "#b5e61d"],
        "Pink": ["#ffaec9"],
        "DarkRed": ["#880015"],
    }
    im = pixels_to_points(
        image_file=EXAMPLE_IMAGE,
        color_keys=color_keys,
        color_threshold=5,
        proximity_grouping=10,
    )

    # check outputs exist
    assert isinstance(im, Image.Image)
    results_path = EXAMPLE_IMAGE.parent / EXAMPLE_IMAGE.stem
    assert (results_path / EXAMPLE_IMAGE.name).exists()
    for k in color_keys:
        assert (results_path / f"{k}.dat").exists()

    # remove generated files
    nuke_directory(results_path)
