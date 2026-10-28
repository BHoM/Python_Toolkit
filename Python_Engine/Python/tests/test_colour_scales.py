import json

import numpy as np
import pytest
from matplotlib import colormaps
from matplotlib.colors import to_hex

from python_toolkit.plot import palettes
from python_toolkit.plot.colour_scales import (
    ColourScale,
    ColourScaleError,
    load_scales,
    save_scale,
    suggest_thresholds,
)

COMFORT = dict(thresholds=[18, 21, 24], cmap=["#0000ff", "#00ffff", "#00ff00", "#ff0000"],
               labels=["Cold", "Cool", "Comfortable", "Hot"], units="degC")


def colour_of(scale, value):
    cmap, norm = scale.mapping()
    return to_hex(cmap(norm(value)))


# -- palettes ------------------------------------------------------------------

def test_toolkit_palettes_are_always_registered():
    for name, (kind, _safe, _colours) in palettes.CUSTOM.items():
        assert name in colormaps and f"{name}_r" in colormaps
        assert name in palettes.names(kind)
    assert isinstance(colormaps["okabe_ito"], type(colormaps["Set1"]))  # discrete, like the other categorical maps
    assert "okabe_ito" in palettes.names("colourblind") and "ltc_maya" not in palettes.names("colourblind")
    assert "viridis_r" in palettes.names() and "viridis_r" not in palettes.names("continuous")


def test_sample_takes_the_first_colours_of_a_categorical_palette():
    assert palettes.sample("okabe_ito", 3) == ["#e69f00", "#56b4e9", "#009e73"]
    assert palettes.sample("magma", 3)[0] == "#000004"
    assert len(palettes.sample("traffic_light", 7)) == 7 and len(palettes.sample("viridis", 1)) == 1


# -- thresholds hold in data units, whatever data is passed in ----------------

def test_bands_hold_in_data_units():
    scale = ColourScale("Comfort", **COMFORT)
    assert colour_of(scale, 17.99) == "#0000ff"
    assert colour_of(scale, 18.0) == "#00ffff"  # boundary belongs to the band above
    assert colour_of(scale, 22.0) == "#00ff00"
    assert colour_of(scale, 24.0) == "#ff0000"
    assert colour_of(scale, -1000) == "#0000ff" and colour_of(scale, 1000) == "#ff0000"


def test_band_labels():
    assert ColourScale("Comfort", **COMFORT).band_labels() == ["Cold", "Cool", "Comfortable", "Hot"]
    plain = ColourScale("Plain", [10, 20], "viridis")
    assert plain.band_labels() == ["< 10", "10 - 20", ">= 20"]
    assert ColourScale("Partly", [10, 20], "viridis", labels=["Low", None, ""]).band_labels() == ["Low", "10 - 20", ">= 20"]


def test_changing_the_palette_keeps_the_breaks():
    scale = ColourScale("Heat", [10, 20, 30], "viridis")
    assert scale.colours() == palettes.sample("viridis", 4)
    scale.cmap = "okabe_ito"
    assert scale.thresholds == [10, 20, 30] and scale.colours() == palettes.sample("okabe_ito", 4)
    scale.cmap = ["red", "green", "blue", "black"]
    assert scale.colours()[0] == "#ff0000"
    with pytest.raises(ColourScaleError, match="4 bands"):
        scale.cmap = ["red", "green"]


def test_value_range_follows_the_data_or_the_thresholds():
    scale = ColourScale("T", [10, 20], "viridis")
    assert scale.value_range([12, 18]) == (12, 18) and scale.value_range([5, 5]) == (4.5, 5.5)
    lo, hi = scale.value_range()
    assert lo < 10 and hi > 20


@pytest.mark.parametrize("kwargs,message", [
    (dict(thresholds=[]), "at least one"),
    (dict(thresholds=[2, 1]), "increasing"),
    (dict(thresholds=[1, 2], cmap=["red", "green"]), "3 bands"),
    (dict(thresholds=[1], labels=["a"]), "one label per band"),
    (dict(thresholds=[1], cmap=["red", "notacolour"]), "not a colour"),
    (dict(thresholds=[1], cmap="no_such_map"), "Unknown colour map"),
    (dict(thresholds=[1], name=" "), "needs a name"),
])
def test_validation(kwargs, message):
    with pytest.raises(ColourScaleError, match=message):
        ColourScale(**{"name": "Bad", **kwargs})


# -- suggesting thresholds -----------------------------------------------------

def test_suggest_thresholds_methods():
    data = np.concatenate([np.full(90, 20.0), np.linspace(20, 30, 10)])
    assert suggest_thresholds([0, 100], 4, "equal") == [25, 50, 75]
    assert suggest_thresholds([0.3, 9.7], 5, "nice") == [2, 4, 6, 8]
    with pytest.raises(ColourScaleError, match="repeated values"):
        suggest_thresholds(data, 4, "quantile")
    q = suggest_thresholds(np.arange(100), 4, "quantile")
    assert len(q) == 3 and q[0] < q[1] < q[2]
    assert suggest_thresholds([1, None, "x", float("nan"), 3], 2, "equal") == [2]


def test_log_thresholds_have_equal_ratios():
    thresholds = suggest_thresholds([1, 1000], 3, "log")
    assert thresholds == pytest.approx([10, 100])
    spread = suggest_thresholds(np.geomspace(0.5, 4000, 50), 5, "log")
    ratios = [b / a for a, b in zip(spread, spread[1:])]
    assert len(spread) == 4 and ratios == pytest.approx([ratios[0]] * 3, rel=0.02)
    for data in ([0, 10, 100], [-5, 10, 100]):
        with pytest.raises(ColourScaleError, match="above zero"):
            suggest_thresholds(data, 3, "log")
    with pytest.raises(ColourScaleError, match="too narrow"):
        suggest_thresholds([1.0, 1.001], 5, "log")


@pytest.mark.parametrize("data,bands,expected", [
    ([16, 30], 5, [17.5, 20, 22.5, 25]),
    ([8, 24], 4, [10, 15, 20]),
    ([0, 95], 4, [25, 50, 75]),
    ([1000, 250000], 5, [50000, 100000, 150000, 200000]),
])
def test_nice_thresholds_fall_inside_the_data(data, bands, expected):
    thresholds = suggest_thresholds(data, bands, "nice")
    assert thresholds == pytest.approx(expected)
    assert all(min(data) < t < max(data) for t in thresholds)


# -- saved scales --------------------------------------------------------------

def test_round_trip_through_dict():
    for scale in (ColourScale("Comfort", **COMFORT), ColourScale("Palette", [1, 2], cmap="ltc_maya")):
        assert ColourScale.from_dict(json.loads(json.dumps(scale.to_dict()))).to_dict() == scale.to_dict()


def test_save_and_load(tmp_path):
    path = tmp_path / "scales.json"
    save_scale(ColourScale("Comfort", **COMFORT), path)
    save_scale(ColourScale("Overheating", [26, 28], "RdYlGn_r"), path)
    assert [s.name for s in load_scales(path)] == ["Comfort", "Overheating"]
    with pytest.raises(ColourScaleError, match="already exists"):
        save_scale(ColourScale("Comfort", [1], "viridis"), path)
    save_scale(ColourScale("Comfort", [1], "viridis"), path, overwrite=True)
    assert load_scales(path)[-1].thresholds == [1]


def test_unreadable_entries_are_skipped_and_kept(tmp_path):
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps({"scales": [
        ColourScale("Good", [1], "viridis").to_dict(),
        {"name": "Broken", "thresholds": [2, 1], "cmap": "viridis"},
    ]}), encoding="utf-8")
    assert [s.name for s in load_scales(path)] == ["Good"]
    save_scale(ColourScale("New", [5], "viridis"), path)
    assert "Broken" in [e["name"] for e in json.loads(path.read_text(encoding="utf-8"))["scales"]]


def test_entries_without_thresholds_are_skipped(tmp_path):
    path = tmp_path / "gradient.json"
    path.write_text(json.dumps({"scales": [{"type": "gradient", "name": "Old gradient", "stops": [[0, "red"], [1, "blue"]]}]}),
                    encoding="utf-8")
    assert load_scales(path) == []


def test_older_threshold_entries_still_load(tmp_path):
    path = tmp_path / "old.json"
    path.write_text(json.dumps({"version": 1, "scales": [
        {"type": "thresholds", "name": "Old", "thresholds": [1], "colours": ["#000000", "#ffffff"],
         "labels": None, "units": None, "group": "TM59"},
    ]}), encoding="utf-8")
    assert load_scales(path)[0].colours() == ["#000000", "#ffffff"]


def test_corrupt_file_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ColourScaleError, match="Cannot read"):
        load_scales(path)


@pytest.mark.parametrize("method", ["equal", "quantile", "nice", "log"])
@pytest.mark.parametrize("bands", [2, 3, 4, 5, 6, 8])
def test_suggestions_always_give_the_number_of_bands_asked_for(method, bands):
    data = np.random.default_rng(1).normal(22, 3, 300)
    assert len(suggest_thresholds(data, bands, method)) == bands - 1
    assert len(suggest_thresholds([16, 30], bands, "nice")) == bands - 1
