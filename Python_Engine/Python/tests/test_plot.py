import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from python_toolkit.plot.diurnal import diurnal, stacked_diurnals
from python_toolkit.plot.heatmap import heatmap
from python_toolkit.plot.polar import polar
from python_toolkit.plot.spatial_heatmap import spatial_heatmap
from python_toolkit.plot.utilities import (
    colormap_sequential,
    contrasting_colour,
    create_triangulation,
    lighten_color,
    relative_luminance
)
from matplotlib.figure import Figure

from pathlib import Path
from . import TEST_DATA, TIMESERIES_COLLECTION

def test_create_triangulation():
    """_"""
    # Test with valid input
    x, y = np.meshgrid(range(10), range(10))
    triang = create_triangulation(x.flatten(), y.flatten())
    assert len(triang.triangles) == 162

    # Test with invalid input
    x = [0, 1, 2, 3, 4, 5]
    y = [0, 1, 2, 3, 4]
    with pytest.raises(ValueError):
        create_triangulation(x, y)

    # Test with alpha value that is too small
    x, y = np.meshgrid(range(0, 100, 10), range(0, 100, 10))
    with pytest.raises(ValueError):
        create_triangulation(x, y, alpha=0.00001)

def test_relative_luminance():
    """_"""
    assert relative_luminance("#FFFFFF") == pytest.approx(1.0, rel=1e-7)
    assert relative_luminance("#000000") == pytest.approx(0.0, rel=1e-7)
    assert relative_luminance("#808080") == pytest.approx(0.215860500965604, rel=1e-7)


def test_contrasting_color():
    """_"""
    assert contrasting_colour("#FFFFFF") == ".15"
    assert contrasting_colour("#000000") == "w"
    assert contrasting_colour("#808080") == "w"


def test_lighten_color():
    """_"""
    # Test lightening a named color
    assert lighten_color("g", 0.3) == (
        0.5500000000000002,
        0.9999999999999999,
        0.5500000000000002,
    )

    # Test lightening a hex color
    assert lighten_color("#F034A3", 0.6) == (
        0.9647058823529411,
        0.5223529411764707,
        0.783529411764706,
    )

    # Test lightening an RGB color
    assert lighten_color((0.3, 0.55, 0.1), 0.5) == (
        0.6365384615384615,
        0.8961538461538462,
        0.42884615384615377,
    )

    # Test lightening a color by 0
    assert lighten_color("g", 0) == (1.0, 1.0, 1.0)

    # Test lightening a color by 1
    assert lighten_color("g", 1) == (0.0, 0.5, 0.0)


def test_colormap_sequential():
    """_"""
    assert sum(colormap_sequential("red", "green", "blue")(0.25)) == pytest.approx(1.750003844675125, rel=0.01)

def test_spatial_heatmap():
    """_"""
    x = np.linspace(0, 100, 101)
    y = np.linspace(0, 100, 101)
    xx, yy = np.meshgrid(x, y)
    zz = (np.sin(xx) * np.cos(yy)).flatten()
    tri = create_triangulation(xx.flatten(), yy.flatten())
    assert isinstance(spatial_heatmap([tri], [zz], contours=[0]), plt.Figure)
    plt.close("all")

#TODO: use a preset collection, or generate one from a year and random values
def test_timeseries_diurnal():
    """_"""
    assert isinstance(diurnal(TIMESERIES_COLLECTION), plt.Axes)
    assert isinstance(
        diurnal(TIMESERIES_COLLECTION, period="daily"),
        plt.Axes,
    )
    assert isinstance(
        diurnal(TIMESERIES_COLLECTION, period="weekly"),
        plt.Axes,
    )
    assert isinstance(
        diurnal(TIMESERIES_COLLECTION, period="monthly"),
        plt.Axes,
    )
    with pytest.raises(ValueError):
        diurnal(TIMESERIES_COLLECTION, period="decadely")
        diurnal(
            TIMESERIES_COLLECTION.reset_index(drop=True),
            period="monthly",
        )
        diurnal(
            TIMESERIES_COLLECTION,
            period="monthly",
            minmax_range=[0.95, 0.05],
        )
        diurnal(
            TIMESERIES_COLLECTION,
            period="monthly",
            quantile_range=[0.95, 0.05],
        )
    plt.close("all")

    assert isinstance(
        stacked_diurnals(
            datasets=[
                TIMESERIES_COLLECTION,
                TIMESERIES_COLLECTION,
            ]
        ),
        plt.Figure,
    )

def test_heatmap():
    """_"""
    assert isinstance(heatmap(TIMESERIES_COLLECTION), plt.Axes)
    plt.close("all")

    mask = np.random.random(8760) > 0.5
    assert isinstance(heatmap(TIMESERIES_COLLECTION, mask=mask), plt.Axes)
    plt.close("all")

    mask_bad = np.random.random(10) > 0.5
    with pytest.raises(ValueError):
        heatmap(TIMESERIES_COLLECTION, mask=mask_bad)
    plt.close("all")

    assert isinstance(
        heatmap(
            pd.Series(
                np.random.random(21000),
                index=pd.date_range("2000-01-01", periods=21000, freq="h"),
            )
        ),
        plt.Axes,
    )
    plt.close("all")

def test_polar():
    """_"""
    assert isinstance(polar(TEST_DATA), plt.Axes)
    plt.close("all")

    