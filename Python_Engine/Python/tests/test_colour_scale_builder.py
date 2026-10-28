import numpy as np
import pytest

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets.custom_cmap_builder import CmapBuilder
from python_toolkit.bhom_tkinter.windows import ColourScaleBuilder
from python_toolkit.bhom_tkinter.windows.colour_scale_builder import GRADIENT, preview_figure
from python_toolkit.plot.colour_scales import ColourScaleLibrary, DataSummary, GradientScale, ThresholdScale


@pytest.fixture
def host():
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
    return ColourScaleLibrary(tmp_path / "scales.json")


def test_builder_suggests_bands_from_data(host, library):
    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 200), units="degC", library=library)
    scale = builder.current_scale()
    assert isinstance(scale, ThresholdScale)
    assert scale.thresholds == pytest.approx([17.5, 20, 22.5, 25])
    assert scale.units == "degC"
    assert "200 values from 16 to 30 degC" in builder.data_text.get()


def test_builder_saves_labels_into_a_set(host, library):
    saved = []
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library=library, on_save=saved.append)
    builder.name.set("Comfort")
    builder.group.value_var.set("Overheating")  # typed into the editable set box
    builder._band_rows[0]["label"].set("Cold")
    builder._save()
    reopened = ColourScaleLibrary(library.path)
    scale = reopened.get("Comfort")
    assert saved and saved[0].name == "Comfort"
    assert scale.group == "Overheating" and scale.band_labels()[0] == "Cold"


def test_builder_reports_bad_thresholds_without_saving(host, library, warnings_shown):
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library=library)
    builder._band_rows[0]["upper"].set("warm")
    builder._save()
    assert builder.saved_scale is None and "not a number" in builder.status.get()
    assert warnings_shown and "not a number" in warnings_shown[0][0]  # shown in a pop-up, not only in the window
    assert len(library) == 0


def test_builder_name_clash_is_explained_and_default_names_are_free(host, library, warnings_shown):
    library.save(ThresholdScale("New scale", [1, 2], ["#000000", "#808080", "#ffffff"]))
    builder = ColourScaleBuilder(host, data=[18, 21, 24, 27], library=library)
    assert builder.name.get() == "New scale 2"
    builder.name.set("New scale")
    builder._save()
    assert builder.saved_scale is None and "another name" in warnings_shown[-1][0]
    builder.name.set("Renamed")
    builder._update_preview()  # what the name change schedules
    assert builder.status.get() == ""  # the old error does not linger


def test_builder_gradient_and_edit(host, library):
    builder = ColourScaleBuilder(host, data=[0, 1, 2], library=library)
    builder.kind.set(GRADIENT)
    builder._on_kind_changed()
    assert isinstance(builder.current_scale(), GradientScale)
    existing = ThresholdScale("Existing", [1, 2], ["#000000", "#808080", "#ffffff"], labels=["a", "b", "c"])
    editor = ColourScaleBuilder(host, scale=existing, library=library)
    assert editor.current_scale().band_labels() == ["a", "b", "c"]


def test_preview_with_and_without_data():
    scale = ThresholdScale("T", [20, 25], ["#0000ff", "#00ff00", "#ff0000"])
    values = np.linspace(16, 30, 50)
    assert preview_figure(scale, values, DataSummary.from_data(values)).axes
    assert preview_figure(scale, np.array([]), None).axes


def test_cmap_builder_reports_saved_scale_as_colormap(host):
    received = []
    widget = CmapBuilder(host.content_frame, command=lambda cmap, bounds: received.append((cmap, bounds)))
    widget._on_saved(ThresholdScale("T", [20, 25], ["#0000ff", "#00ff00", "#ff0000"]))
    cmap, bounds = received[0]
    assert widget.get() is cmap and widget.get_bounds() == bounds and bounds[0] < 20 < 25 < bounds[1]
    assert widget.get_scale().name == "T"


def test_builder_starts_from_a_colour_map_and_recolours(host, library):
    from python_toolkit.plot.colour_scales import palette_colours

    builder = ColourScaleBuilder(host, data=np.linspace(16, 30, 50), library=library, palette="magma")
    assert builder.palette.get() == "magma"
    assert [r["colour"].get() for r in builder._band_rows] == palette_colours("magma", 5)
    builder.palette.set("Traffic light")
    builder._recolour()
    scale = builder.current_scale()
    assert scale.colours == palette_colours("Traffic light", 5) and scale.thresholds == pytest.approx([17.5, 20, 22.5, 25])
