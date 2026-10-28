import numpy as np
import pytest
from matplotlib.colors import to_hex

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets.cmap_selector import CmapSelector
from python_toolkit.bhom_tkinter.windows import ColourScaleBuilder
from python_toolkit.bhom_tkinter.windows.colour_scale_builder import preview_figure
from python_toolkit.plot import palettes
from python_toolkit.plot.colour_scales import ColourScale, load_scales, save_scale


@pytest.fixture(scope="module")
def host():
    """One Tk root for the module: creating a Tk root per test intermittently fails to start Tcl on Windows."""
    root = BHoMBaseWindow(title="Builder host", show_submit=False, show_close=False)
    root.withdraw()
    yield root
    root.destroy_root()


@pytest.fixture(autouse=True)
def warnings_shown(monkeypatch):
    """Record warning pop-ups instead of blocking on them."""
    from python_toolkit.bhom_tkinter.windows import colour_scale_builder

    shown = []

    class _Box:
        def __init__(self, title, errors, parent=None):
            shown.append(errors)

        def build(self):
            pass

        def run(self):
            pass

    monkeypatch.setattr(colour_scale_builder, "WarningBox", _Box)
    return shown


@pytest.fixture
def library(tmp_path):
    return tmp_path / "scales.json"


def test_builder_suggests_bands_from_data(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), units="degC", library_path=library)
    scale = builder.current_scale()
    assert scale.thresholds == pytest.approx([17.5, 20, 25, 27.5])
    assert scale.units == "degC" and scale.cmap == "viridis"
    assert "200 values from 16 to 30 degC" in builder.data_text.get()


def test_builder_saves_labels(host, library):
    saved = []
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library_path=library, on_save=saved.append)
    builder.name.set("Comfort")
    builder._band_rows[0]["label"].set("Cold")
    builder._save()
    scale = load_scales(library)[0]
    assert saved and saved[0].name == "Comfort"
    assert scale.name == "Comfort" and scale.band_labels()[0] == "Cold"


def test_builder_reports_bad_thresholds_without_saving(host, library, warnings_shown):
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library_path=library)
    builder._band_rows[0]["upper"].set("warm")
    builder._save()
    assert builder.saved_scale is None and "not a number" in builder.status.get()
    assert warnings_shown and "not a number" in warnings_shown[0][0]  # shown in a pop-up, not only in the window
    assert load_scales(library) == []


def test_builder_name_clash_is_explained_and_default_names_are_free(host, library, warnings_shown):
    save_scale(ColourScale("New scale", [1, 2], "viridis"), library)
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library_path=library)
    assert builder.name.get() == "New scale 2"
    builder.name.set("New scale")
    builder._save()
    assert builder.saved_scale is None and "another name" in warnings_shown[-1][0]
    builder.name.set("Renamed")
    builder._update_preview()  # what the name change schedules
    assert builder.status.get() == ""  # the old error does not linger


def test_builder_log_breaks_and_edit(host, library):
    builder = ColourScaleBuilder(host, data=np.geomspace(1, 1000, 100), library_path=library)
    builder.method.set("log")
    builder.band_count.set(3)
    builder._suggest()
    assert builder.current_scale().thresholds == pytest.approx([10, 100])
    existing = ColourScale("Existing", [1, 2], ["#000000", "#808080", "#ffffff"], labels=["a", "b", "c"])
    editor = ColourScaleBuilder(host, scale=existing, library_path=library)
    assert editor.current_scale().band_labels() == ["a", "b", "c"]
    assert editor.current_scale().cmap == ["#000000", "#808080", "#ffffff"]


def test_preview_with_and_without_data():
    scale = ColourScale("T", [20, 25], ["#0000ff", "#00ff00", "#ff0000"])
    assert preview_figure(scale, np.linspace(16, 30, 50)).axes
    assert preview_figure(scale, np.array([])).axes


def test_builder_starts_from_a_palette_and_recolours(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 50), library_path=library, palette="magma")
    assert builder.palette.get() == "magma"
    assert [r["colour"].get() for r in builder._band_rows] == palettes.sample("magma", 5)
    assert builder.current_scale().cmap == "magma"  # untouched band colours stay a palette reference
    builder.palette.set("traffic_light")
    builder._recolour()
    scale = builder.current_scale()
    assert scale.cmap == "traffic_light" and scale.thresholds == pytest.approx([17.5, 20, 25, 27.5])
    builder._band_rows[0]["colour"].set("#123456")
    assert builder.current_scale().cmap[0] == "#123456"  # a hand-picked colour makes it an explicit list


def test_cmap_selector_lists_palette_sets(host):
    for cmap_set, expected in (("categorical", "okabe_ito"), ("colourblind", "okabe_ito"), ("continuous", "ltc_maya")):
        values = list(CmapSelector(host.content_frame, cmap_set=cmap_set).cmap_combobox["values"])
        assert expected in values and f"{expected}_r" in values
    assert "okabe_ito" not in CmapSelector(host.content_frame, cmap_set="continuous").cmap_combobox["values"]


def test_cmap_selector_lists_what_it_is_given(host):
    selector = CmapSelector(host.content_frame, colormaps=["viridis"])
    assert list(selector.cmap_combobox["values"]) == ["viridis"]


def test_end_to_end_palette_to_saved_scale_to_colours(host, library):
    """Pick a colour-blind palette in the selector, build a scale from data, save it, reload it and colour with it."""
    data = np.linspace(16, 30, 100)
    selector = CmapSelector(host.content_frame, cmap_set="colourblind", default_cmap="okabe_ito")
    assert selector.get() == "okabe_ito"

    builder = ColourScaleBuilder(host, data=data, library_path=library, palette=selector.get())
    builder.name.set("Comfort")
    builder._save()

    scale = load_scales(library)[0]
    assert scale.cmap == "okabe_ito" and scale.thresholds == pytest.approx([17.5, 20, 25, 27.5])
    cmap, norm = scale.mapping()
    colours = {to_hex(cmap(norm(v))) for v in data}
    assert colours == set(palettes.sample("okabe_ito", 5))  # every band is used, in the palette's colours

    scale.cmap = "viridis"  # swap the colours; the breaks hold
    assert scale.thresholds == pytest.approx([17.5, 20, 25, 27.5]) and scale.colours() == palettes.sample("viridis", 5)


def test_bands_and_breaks_update_the_scale_without_a_button(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    assert len(builder._band_rows) == 5
    builder.band_count.set(3)  # what the spinbox does when changed
    builder._run_auto_suggest()  # what fires once typing has paused
    assert len(builder._band_rows) == 3 and builder.current_scale().thresholds == pytest.approx([20, 25])
    builder.method.set("equal")
    builder.method.combobox.event_generate("<<ComboboxSelected>>")
    builder._run_auto_suggest()
    assert builder.current_scale().thresholds == pytest.approx([20.6667, 25.3333], abs=1e-3)
    assert len(builder._band_rows) == 3 and builder.band_count.get() == 3  # showing the count does not loop


def test_typing_in_bands_waits_for_the_pause(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    builder.band_count.set("1")  # first keystroke of "12": nothing happens yet
    assert len(builder._band_rows) == 5 and builder._suggest_job is not None
    builder.band_count.set("12")
    builder._run_auto_suggest()
    assert len(builder._band_rows) == 12
    builder.band_count.set("99")  # out of range: ignored, bands stay as they are
    builder._run_auto_suggest()
    assert len(builder._band_rows) == 12


def test_bands_and_breaks_are_locked_without_data(host, library):
    builder = ColourScaleBuilder(host, library_path=library)
    assert str(builder.band_count.spinbox.cget("state")) == "disabled"
    assert str(builder.method.combobox.cget("state")) == "disabled"


def test_changing_the_bands_keeps_what_was_filled_in(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    for i, name in enumerate(["Cold", "Cool", "Comfy", "Warm"]):
        builder._band_rows[i]["label"].set(name)
    builder._band_rows[1]["colour"].set("#123456")
    builder.band_count.set(4)
    builder._run_auto_suggest()
    scale = builder.current_scale()
    assert scale.bands == 4 and scale.labels == ["Cold", "Cool", "Comfy", "Warm"]
    assert scale.colours()[1] == "#123456"  # the hand-picked colour stays
    builder.band_count.set(6)  # new bands start empty and take palette colours
    builder._run_auto_suggest()
    scale = builder.current_scale()
    assert scale.labels[:4] == ["Cold", "Cool", "Comfy", "Warm"] and scale.labels[4:] == [None, None]
    assert scale.colours()[1] == "#123456" and scale.colours()[5] == palettes.sample("viridis", 6)[5]


def test_changing_the_bands_recolours_untouched_colours(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    builder.band_count.set(3)
    builder._run_auto_suggest()
    assert builder.current_scale().cmap == "viridis"  # still a palette reference, resampled for 3 bands


def test_thresholds_spin_in_round_steps(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    spin = builder._band_rows[0]["upper"].spinbox
    assert float(spin.cget("increment")) == 0.1  # about 1% of the 14-wide range, rounded
    for _ in range(5):
        spin.event_generate("<<Increment>>")
    assert builder.current_scale().thresholds[0] == pytest.approx(17.5 + 0.5)


def test_split_a_band_adds_one_between_its_ends(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)  # breaks 17.5 20 25 27.5
    builder._band_rows[1]["label"].set("Cool")
    builder._split_band(1)  # the band 17.5 to 20 becomes 17.5 to 18.75 and 18.75 to 20
    scale = builder.current_scale()
    assert scale.thresholds == pytest.approx([17.5, 18.75, 20, 25, 27.5]) and scale.bands == 6
    assert scale.labels == [None, "Cool", None, None, None, None]  # the label stays with the lower half
    assert builder.band_count.get() == 6
    assert scale.cmap == "viridis"  # still a palette, spread over six bands


def test_split_the_open_ends_against_the_data(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    builder._split_band(0)  # below 17.5: split against the data minimum, 16
    assert builder.current_scale().thresholds[:2] == pytest.approx([16.75, 17.5])
    builder._split_band(len(builder._band_rows) - 1)  # 27.5 and above: split against the data maximum, 30
    assert builder.current_scale().thresholds[-1] == pytest.approx(28.75)


def test_remove_a_band_merges_its_range_into_the_next(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    for i, name in enumerate(["a", "b", "c", "d", "e"]):
        builder._band_rows[i]["label"].set(name)
    builder._band_rows[2]["colour"].set("#123456")  # a hand-picked colour, which makes colours explicit
    builder._remove_band(1)
    scale = builder.current_scale()
    assert scale.thresholds == pytest.approx([17.5, 25, 27.5]) and scale.labels == ["a", "c", "d", "e"]  # "c" now starts at 17.5
    assert scale.colours()[1] == "#123456"
    builder._remove_band(len(builder._band_rows) - 1)  # the last band: the one before it becomes open-ended
    assert builder.current_scale().thresholds == pytest.approx([17.5, 25]) and builder.current_scale().labels == ["a", "c", "d"]


def test_bands_cannot_go_below_two_or_above_the_maximum(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    builder.band_count.set(2)
    builder._run_auto_suggest()
    assert "disabled" in builder._band_rows[0]["remove"].state()
    builder._remove_band(0)
    assert len(builder._band_rows) == 2
    builder.band_count.set(24)
    builder._run_auto_suggest()
    assert "disabled" in builder._band_rows[0]["split"].state()
    builder._split_band(0)
    assert len(builder._band_rows) == 24


def test_split_refuses_a_bad_threshold_without_changing_the_table(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), library_path=library)
    builder._band_rows[0]["upper"].set("warm")
    builder._split_band(1)
    assert len(builder._band_rows) == 5 and "not a number" in builder.status.get()
