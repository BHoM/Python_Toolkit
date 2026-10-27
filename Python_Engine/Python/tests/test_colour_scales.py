import json

import numpy as np
import pytest
from matplotlib.colors import to_hex

from python_toolkit.bhom import custom_cmaps
from python_toolkit.plot.colour_scales import (
    ColourScale,
    ColourScaleError,
    ColourScaleLibrary,
    DataSummary,
    GradientScale,
    PALETTES,
    ThresholdScale,
    palette_colours,
    suggest_thresholds,
)

COMFORT = dict(thresholds=[18, 21, 24], colours=["#0000ff", "#00ffff", "#00ff00", "#ff0000"],
               labels=["Cold", "Cool", "Comfortable", "Hot"], units="degC", group="TM59")


def colour_of(mapping, value):
    return to_hex(mapping.cmap(mapping.norm(value)))


# -- thresholds hold in data units, whatever data is passed in ----------------

@pytest.mark.parametrize("data", [[19, 20, 22], np.linspace(-50, 200, 30), [23.9], None])
def test_bands_fixed_for_any_data(data):
    mapping = ThresholdScale("Comfort", **COMFORT).mapping(data)
    assert colour_of(mapping, 17.99) == "#0000ff"
    assert colour_of(mapping, 18.0) == "#00ffff"  # boundary belongs to the band above
    assert colour_of(mapping, 22.0) == "#00ff00"
    assert colour_of(mapping, 24.0) == "#ff0000"
    assert colour_of(mapping, -1000) == "#0000ff" and colour_of(mapping, 1000) == "#ff0000"
    assert mapping.band_labels == ["Cold", "Cool", "Comfortable", "Hot"]


def test_auto_band_labels_and_band_of():
    scale = ThresholdScale("Plain", [10, 20], ["red", "green", "blue"])
    assert scale.band_labels() == ["< 10", "10 - 20", ">= 20"]
    assert [scale.band_of(v) for v in (5, 10, 19.9, 20, 99)] == [0, 1, 1, 2, 2]
    partly = ThresholdScale("Partly", [10, 20], ["red", "green", "blue"], labels=["Low", None, ""])
    assert partly.band_labels() == ["Low", "10 - 20", ">= 20"]


@pytest.mark.parametrize("kwargs,message", [
    (dict(thresholds=[], colours=["red"]), "at least one"),
    (dict(thresholds=[2, 1], colours=["r", "g", "b"]), "increasing"),
    (dict(thresholds=[1, 2], colours=["red", "green"]), "3 bands"),
    (dict(thresholds=[1], colours=["red", "green"], labels=["a"]), "one label per band"),
    (dict(thresholds=[1], colours=["red", "notacolour"]), "not a colour"),
])
def test_threshold_validation(kwargs, message):
    with pytest.raises(ColourScaleError, match=message):
        ThresholdScale("Bad", **kwargs)


def test_gradient_relative_stretches_to_data_absolute_does_not():
    relative = GradientScale.from_palette("Rel", "Traffic light")
    assert relative.mapping([10, 30]).norm.vmin == 10 and relative.mapping([10, 30]).norm.vmax == 30
    absolute = GradientScale("Abs", [(0, "blue"), (100, "red")], relative=False)
    assert (absolute.mapping([10, 30]).norm.vmin, absolute.mapping([10, 30]).norm.vmax) == (0, 100)
    stepped = GradientScale("Steps", [(0, "blue"), (1, "red")], bins=4).mapping([0, 8])
    assert len({colour_of(stepped, v) for v in np.linspace(0, 8, 50)}) == 4
    with pytest.raises(ColourScaleError):
        GradientScale("Bad", [(0, "red"), (2, "blue")], relative=True)


def test_mapping_colours_for_handles_missing_values():
    rgba = ThresholdScale("C", **COMFORT).mapping().colours_for([17, None, "x", 30])
    assert np.isnan(rgba[1]).all() and np.isnan(rgba[2]).all()
    assert to_hex(rgba[3]) == "#ff0000"


# -- data passed in ----------------------------------------------------------

def test_data_summary_ignores_unreadable_values():
    summary = DataSummary.from_data([1, 2, None, "n/a", float("nan"), 3, 10])
    assert summary.count == 4 and summary.minimum == 1 and summary.maximum == 10
    assert summary.histogram[0].sum() == 4
    with pytest.raises(ColourScaleError):
        DataSummary.from_data([None, "x"])


def test_suggest_thresholds_methods():
    data = np.concatenate([np.full(90, 20.0), np.linspace(20, 30, 10)])
    assert suggest_thresholds([0, 100], 4, "equal") == [25, 50, 75]
    assert suggest_thresholds([0.3, 9.7], 5, "nice") == [2, 4, 6, 8]
    with pytest.raises(ColourScaleError, match="repeated values"):
        suggest_thresholds(data, 4, "quantile")
    q = suggest_thresholds(np.arange(100), 4, "quantile")
    assert len(q) == 3 and q[0] < q[1] < q[2]


def test_threshold_scale_from_data():
    scale = ThresholdScale.from_data("Loads", np.linspace(0, 95, 50), bands=4, method="nice",
                                     palette="Okabe-Ito (colour-blind safe)", group="Loads")
    assert scale.thresholds == [25, 50, 75] and scale.bands == 4 and scale.group == "Loads"
    assert len(palette_colours("Traffic light", 7)) == 7


# -- persistence -------------------------------------------------------------

def test_round_trip_through_dict():
    for scale in (ThresholdScale("Comfort", **COMFORT), GradientScale.from_palette("G", "LTC Maya", bins=6)):
        rebuilt = ColourScale.from_dict(json.loads(json.dumps(scale.to_dict())))
        assert type(rebuilt) is type(scale) and rebuilt.to_dict() == scale.to_dict()


def test_library_sets(tmp_path):
    library = ColourScaleLibrary(tmp_path / "scales.json")
    library.save(ThresholdScale("Comfort", **COMFORT))
    library.save(GradientScale.from_palette("Heat", "LTC Heatmap", group="Loads"))
    library.save(ThresholdScale("Overheating", [26, 28], ["green", "orange", "red"], group="TM59"))
    reopened = ColourScaleLibrary(tmp_path / "scales.json")
    assert reopened.groups() == ["TM59", "Loads"]
    assert reopened.names("TM59") == ["Comfort", "Overheating"]
    assert reopened.get("Comfort").labels[-1] == "Hot"
    with pytest.raises(ColourScaleError, match="already exists"):
        reopened.save(ThresholdScale("Comfort", **COMFORT))
    reopened.rename_group("TM59", "Overheating checks")
    reopened.delete_group("Loads")
    final = ColourScaleLibrary(tmp_path / "scales.json")
    assert final.groups() == ["Overheating checks"] and len(final) == 2


def test_library_reads_original_format(tmp_path):
    path = tmp_path / "old.json"
    path.write_text(json.dumps([
        {"name": "OldBins", "type": "bins", "vmin": 0, "vmax": 30,
         "colours": ["#0000ff", "#00ff00", "#ff0000"], "positions": [0, 10, 20]},
        {"name": "OldGrad", "type": "interpolation", "vmin": 0, "vmax": 5,
         "colours": ["#000000", "#ffffff"], "positions": [0, 5]},
    ]), encoding="utf-8")
    library = ColourScaleLibrary(path)
    bins = library.get("OldBins")
    assert isinstance(bins, ThresholdScale) and bins.thresholds == [10, 20]
    assert colour_of(bins.mapping(), 25) == "#ff0000"
    grad = library.get("OldGrad")
    assert isinstance(grad, GradientScale) and grad.mapping().norm.vmax == 5


def test_unreadable_entries_reported_and_kept(tmp_path):
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps({"version": 2, "scales": [
        ThresholdScale("Good", [1], ["red", "blue"]).to_dict(),
        {"type": "thresholds", "name": "Broken", "thresholds": [2, 1], "colours": ["a"]},
    ]}), encoding="utf-8")
    library = ColourScaleLibrary(path)
    assert library.names() == ["Good"] and "Broken" in library.problems[0]
    library.save(ThresholdScale("New", [5], ["red", "blue"]))
    names_on_disk = [e["name"] for e in json.loads(path.read_text(encoding="utf-8"))["scales"]]
    assert "Broken" in names_on_disk  # never silently deleted


def test_corrupt_library_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ColourScaleError, match="Cannot read"):
        ColourScaleLibrary(path)


def test_custom_cmaps_wrappers_still_work(tmp_path, monkeypatch):
    from python_toolkit.plot import colour_scales
    monkeypatch.setattr(colour_scales, "LIBRARY_FILE", tmp_path / "c.json")
    custom_cmaps.save_custom_cmap("Bins", "bins", ["#0000ff", "#ff0000"], [0, 50], 0, 100)
    custom_cmaps.save_custom_cmap("Grad", "interpolation", ["#000000", "#ffffff"], [0, 10], 0, 10)
    assert custom_cmaps.list_custom_cmap_names() == ["Bins", "Grad"]
    loaded = {name: (cmap, bounds) for name, cmap, bounds in custom_cmaps.load_custom_cmaps()}
    assert set(loaded) == {"Bins", "Grad"} and loaded["Grad"][1] == (0, 10)
    assert custom_cmaps.delete_custom_cmap("Bins") and not custom_cmaps.delete_custom_cmap("Bins")
    custom_cmaps.clear_custom_cmaps()
    assert custom_cmaps.list_custom_cmap_names() == []


def test_palettes_are_valid():
    for name, colours in PALETTES.items():
        assert len(colours) >= 3, name
        GradientScale.from_palette(name, name)
