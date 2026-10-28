"""Window for building colour scales from the data they will colour.

Pass the data in and the window shows its distribution, suggests band thresholds, and
lets the user colour, label and save the scale into a named set of the colour scale
library (``python_toolkit.plot.colour_scales``)::

    builder = ColourScaleBuilder(parent, data=room_temperatures, units="degC")
    builder.run()
    scale = builder.saved_scale  # None if closed without saving
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, List, Optional

import numpy as np
from matplotlib.figure import Figure

from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow
from python_toolkit.bhom_tkinter.windows.warning_box import WarningBox
from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets.check_box_selection import CheckboxSelection
from python_toolkit.bhom_tkinter.widgets.colour_picker import ColourPicker
from python_toolkit.bhom_tkinter.widgets.drop_down_selection import DropDownSelection
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets.label import Label
from python_toolkit.bhom_tkinter.widgets.radio_selection import RadioSelection
from python_toolkit.bhom_tkinter.widgets.spinbox import Spinbox
from python_toolkit.bhom_tkinter.widgets.validated_entry_box import ValidatedEntryBox
from python_toolkit.plot.colour_scales import (
    DEFAULT_SET,
    PALETTES,
    SUGGESTION_METHODS,
    ColourScale,
    ColourScaleError,
    ColourScaleLibrary,
    DataSummary,
    GradientScale,
    ThresholdScale,
    clean_data,
    palette_colours,
    palette_names,
    suggest_thresholds,
)

THRESHOLDS = "Threshold bands"
GRADIENT = "Gradient"
MAX_BANDS = 12
ERROR_COLOUR = "#c0392b"


class ColourScaleBuilder(BHoMBaseChildWindow):
    """Build, preview and save a ThresholdScale or GradientScale against real data."""

    def __init__(
        self,
        parent=None,
        data: Optional[Iterable] = None,
        units: Optional[str] = None,
        scale: Optional[ColourScale] = None,
        library: Optional[ColourScaleLibrary] = None,
        on_save: Optional[Callable[[ColourScale], None]] = None,
        palette: Optional[str] = None,
        **kwargs,
    ):
        """
        Args:
            parent: Owning window (None for a standalone window).
            data: Values the scale will colour; drives the histogram and suggestions.
            units: Units of the data, stored with the scale.
            scale: An existing scale to edit (saving replaces it).
            library: Library to save into (defaults to the user's library).
            on_save: Called with the saved scale.
            palette: Palette or matplotlib colour map to start from (e.g. the plot's current one).
        """
        self.values = clean_data(data)
        self.summary = DataSummary.from_data(self.values) if self.values.size else None
        self.units = units if units is not None else (scale.units if scale else None)
        self.library = library if library is not None else ColourScaleLibrary()
        self.editing = scale
        self.on_save = on_save
        self.saved_scale: Optional[ColourScale] = None
        self._band_rows: List[dict] = []
        self._pending = None
        self._start_palette = palette
        super().__init__(
            parent,
            title="Colour scale",
            submit_text="Save scale",
            submit_command=self._save,
            close_on_submit=False,
            close_text="Close",
            modal=parent is not None,
            defer_show=True,
            resizable=True,
            min_width=kwargs.pop("min_width", 620),
            min_height=kwargs.pop("min_height", 800),
            **kwargs,
        )
        self._build_contents()
        self.build()
        self._load(scale)

    # ── layout ─────────────────────────────────────────────────────────────

    def _build_contents(self) -> None:
        frame = self.content_frame
        sets = self.library.groups() or [DEFAULT_SET]
        default_set = self.editing.group if self.editing else sets[0]

        self.name = ValidatedEntryBox(frame, id="name", helper_text="Name", required=False, width=30,
                                      on_change=lambda _v: self._schedule_preview(),  # re-checks, clearing old errors
                                      build_options=GridOptions(row=0, column=0, sticky="w", padx=6, pady=3))
        self.group = DropDownSelection(frame, id="group", helper_text="Set (type a new name to start a set)",
                                       options=sets, default=default_set, state="normal", width=28,
                                       build_options=GridOptions(row=0, column=1, sticky="w", padx=6, pady=3))
        self.kind = RadioSelection(frame, id="kind", fields=[THRESHOLDS, GRADIENT], default=THRESHOLDS,
                                   orient="horizontal", command=lambda _v: self._on_kind_changed(),
                                   build_options=GridOptions(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=3))
        self.data_text = Label(frame, text=self._summary_text(),
                               build_options=GridOptions(row=2, column=0, columnspan=2, sticky="w", padx=6))
        self.preview = FigureContainer(frame, id="preview", rigid_width=560, rigid_height=130,
                                       build_options=GridOptions(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=4))

        suggest = ttk.Frame(frame)
        suggest.grid(row=5, column=0, columnspan=2, sticky="w", padx=6, pady=3)
        self.band_count = Spinbox(suggest, id="bands", helper_text="Bands", values=list(range(2, MAX_BANDS + 1)),
                                  default=5, width=5, build_options=GridOptions(row=0, column=0, sticky="w", padx=(0, 8)))
        self.method = DropDownSelection(suggest, id="method", helper_text="Breaks", options=list(SUGGESTION_METHODS),
                                        default="nice", state="readonly", width=10,
                                        build_options=GridOptions(row=0, column=1, sticky="w", padx=(0, 8)))
        palettes = palette_names()
        self.palette = DropDownSelection(suggest, id="palette", helper_text="Palette / colour map", options=palettes,
                                         default=self._start_palette if self._start_palette in palettes else None,
                                         state="readonly", width=28, command=lambda _v: self._recolour(),
                                         build_options=GridOptions(row=0, column=2, sticky="w", padx=(0, 8)))
        self.suggest_button = Button(suggest, text="Suggest from data", command=self._suggest, width=18,
                                     build_options=GridOptions(row=0, column=3, sticky="sw"))
        for widget in (self.band_count, self.method, self.palette, self.suggest_button):
            widget.build()
        if self.summary is None:
            self.suggest_button.button.configure(state="disabled")

        self.bands_frame = ttk.Frame(frame)
        self.bands_frame.grid(row=6, column=0, columnspan=2, sticky="w", padx=6, pady=3)
        self.gradient_frame = ttk.Frame(frame)
        self.gradient_frame.grid(row=6, column=0, columnspan=2, sticky="w", padx=6, pady=3)
        self.reverse = CheckboxSelection(self.gradient_frame, id="reverse", fields=["Reverse"],
                                         command=lambda _v: self._schedule_preview(),
                                         build_options=GridOptions(row=0, column=0, sticky="w", padx=(0, 12)))
        self.steps = Spinbox(self.gradient_frame, id="steps", helper_text="Steps (0 = smooth)",
                             values=[0] + list(range(2, 21)), default=0, width=5,
                             command=lambda _v: self._schedule_preview(),
                             build_options=GridOptions(row=0, column=1, sticky="w"))
        self.reverse.build()
        self.steps.build()

        self.status = Label(frame, text="", foreground=ERROR_COLOUR, wraplength=560, justify="left",
                            build_options=GridOptions(row=4, column=0, columnspan=2, sticky="w", padx=6))
        self.widgets = [self.name, self.group, self.kind, self.data_text, self.preview, self.status]

    def _summary_text(self) -> str:
        if self.summary is None:
            return "No data passed in: set the thresholds by hand."
        s = self.summary
        units = f" {self.units}" if self.units else ""
        return (f"{s.count} values from {s.minimum:.4g} to {s.maximum:.4g}{units}; "
                f"median {s.quartiles[1]:.4g}, middle half {s.quartiles[0]:.4g} to {s.quartiles[2]:.4g}")

    # ── state ──────────────────────────────────────────────────────────────

    def _load(self, scale: Optional[ColourScale]) -> None:
        if isinstance(scale, GradientScale):
            self.name.set(scale.name)
            self.kind.set(GRADIENT)
            self.steps.set(scale.bins or 0)
        elif isinstance(scale, ThresholdScale):
            self.name.set(scale.name)
            self._set_bands(scale.thresholds, scale.colours, scale.labels)
        elif self.summary is not None:
            self.name.set(self._unused_name("New scale"))
            self._suggest()
        else:
            self.name.set(self._unused_name("New scale"))
            self._set_bands([1.0, 2.0], palette_colours(self.palette.get(), 3), None)
        self._on_kind_changed()

    def _on_kind_changed(self) -> None:
        threshold = self.kind.get() == THRESHOLDS
        if threshold:
            self.gradient_frame.grid_remove()
            self.bands_frame.grid()
        else:
            self.bands_frame.grid_remove()
            self.gradient_frame.grid()
        self._schedule_preview()

    def _suggest(self) -> None:
        try:
            bands = int(self.band_count.get())
            thresholds = suggest_thresholds(self.values, bands, self.method.get())
        except (ColourScaleError, ValueError) as e:
            self.status.set(str(e))
            return
        self._set_bands(thresholds, palette_colours(self.palette.get(), len(thresholds) + 1), None)

    def _recolour(self) -> None:
        """A new palette recolours the bands, keeping their thresholds and labels."""
        if not self._band_rows:
            return
        for row, colour in zip(self._band_rows, palette_colours(self.palette.get(), len(self._band_rows))):
            row["colour"].set(colour)
        self._schedule_preview()

    def _set_bands(self, thresholds, colours, labels) -> None:
        for child in self.bands_frame.winfo_children():
            child.destroy()
        self._band_rows = []
        n = len(colours)
        headers = ("Colour", "Label (legend)", "From", "Up to")
        for col, text in enumerate(headers):
            ttk.Label(self.bands_frame, text=text, style="Caption.TLabel").grid(row=0, column=col, sticky="w", padx=4)
        for i in range(n):
            picker = ColourPicker(self.bands_frame, default_colour=colours[i], swatch_width=36, swatch_height=20,
                                  command=lambda _c: self._schedule_preview())
            picker.grid(row=i + 1, column=0, sticky="nw", padx=4, pady=(6, 0))
            label = ValidatedEntryBox(self.bands_frame, required=False, width=22,
                                      on_change=lambda _v: self._schedule_preview())
            label.grid(row=i + 1, column=1, sticky="w", padx=4)
            label.set((labels[i] or "") if labels else "")
            lower = ttk.Label(self.bands_frame, text="")
            lower.grid(row=i + 1, column=2, sticky="nw", padx=4, pady=(6, 0))
            upper = None
            if i < n - 1:
                upper = ValidatedEntryBox(self.bands_frame, required=False, width=10,
                                          on_change=lambda _v: self._schedule_preview())
                upper.grid(row=i + 1, column=3, sticky="w", padx=4)
                upper.set(f"{thresholds[i]:.6g}")
            else:
                ttk.Label(self.bands_frame, text="and above").grid(row=i + 1, column=3, sticky="nw", padx=4, pady=(6, 0))
            self._band_rows.append({"colour": picker, "label": label, "lower": lower, "upper": upper})
        self.band_count.set(n)
        self._schedule_preview()

    def current_scale(self) -> ColourScale:
        """The scale described by the window right now (raises ColourScaleError if invalid)."""
        name = (self.name.get() or "").strip()
        group = (self.group.get() or "").strip() or DEFAULT_SET
        if self.kind.get() == GRADIENT:
            name = self.palette.get()
            colours = PALETTES.get(name) or palette_colours(name, 9)
            if self.reverse.get():
                colours = colours[::-1]
            n = len(colours)
            steps = int(self.steps.get() or 0)
            return GradientScale(name, [(i / (n - 1), c) for i, c in enumerate(colours)], relative=True,
                                 bins=steps or None, units=self.units, group=group)
        thresholds = []
        for i, row in enumerate(self._band_rows[:-1]):
            text = (row["upper"].get() or "").strip()
            try:
                thresholds.append(float(text))
            except ValueError:
                raise ColourScaleError(f"Band {i + 1}: '{text}' is not a number.") from None
        colours = [row["colour"].get() for row in self._band_rows]
        labels = [(row["label"].get() or "").strip() or None for row in self._band_rows]
        return ThresholdScale(name, thresholds, colours, labels=labels if any(labels) else None,
                              units=self.units, group=group)

    def _unused_name(self, base: str) -> str:
        names = set(self.library.names())
        n = 1
        name = base
        while name in names:
            n += 1
            name = f"{base} {n}"
        return name

    def _save(self) -> None:
        """Validate, save to the library and close; errors are shown in a pop-up and stay in the window."""
        try:
            scale = self.current_scale()
            self.library.save(scale, overwrite=self.editing is not None and self.editing.name == scale.name)
        except (ColourScaleError, OSError) as e:
            message = str(e)
            if "already exists" in message:
                message += " Give this scale another name, or edit the saved one instead."
            self.status.set(message)
            box = WarningBox(title="Scale not saved", errors=[message], parent=self)
            box.build()
            box.run()
            return
        CONSOLE_LOGGER.info(f"Saved colour scale '{scale.name}' in set '{scale.group}'.")
        self.saved_scale = scale
        if self.on_save is not None:
            self.on_save(scale)
        self.destroy_root()

    # ── preview ────────────────────────────────────────────────────────────

    def _schedule_preview(self) -> None:
        if self._pending is not None:
            try:
                self.after_cancel(self._pending)
            except tk.TclError:
                pass
        self._pending = self.after(250, self._update_preview)

    def _update_preview(self) -> None:
        self._pending = None
        try:
            scale = self.current_scale()
        except ColourScaleError as e:
            self.status.set(str(e))
            return
        self.status.set("")
        if isinstance(scale, ThresholdScale):
            for row, (lower, _upper) in zip(self._band_rows, scale.band_ranges()):
                row["lower"].configure(text="below" if lower is None else f"{lower:.6g}")
        self.preview.embed_figure(preview_figure(scale, self.values, self.summary))


def preview_figure(scale: ColourScale, values: np.ndarray, summary: Optional[DataSummary]) -> Figure:
    """Histogram of the data over the scale's colours (or the colours alone without data)."""
    fig = Figure(figsize=(5.6, 1.3), dpi=100)
    ax = fig.add_axes([0.04, 0.2, 0.94, 0.76])
    sample = values if values.size else scale.preview_data()
    mapping = scale.mapping(sample)
    lo, hi = (summary.minimum, summary.maximum) if summary else (float(sample.min()), float(sample.max()))
    if lo == hi:
        lo, hi = lo - 0.5, hi + 0.5
    pad = (hi - lo) * 0.04
    xs = np.linspace(lo - pad, hi + pad, 400)
    colours = mapping.cmap(mapping.norm(xs))
    ax.imshow(colours[np.newaxis, :, :], aspect="auto", extent=(xs[0], xs[-1], 0, 1), alpha=0.85,
              origin="lower", zorder=0)
    if summary is not None:
        counts, edges = summary.histogram
        heights = counts / max(counts.max(), 1)
        ax.bar(edges[:-1], heights, width=np.diff(edges), align="edge", color="#202020", alpha=0.55,
               edgecolor="#ffffff", linewidth=0.6, zorder=1)
    if isinstance(scale, ThresholdScale):
        for t in scale.thresholds:
            if xs[0] <= t <= xs[-1]:
                ax.axvline(t, color="#000000", linewidth=1.2, zorder=2)
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(0, 1.05)
    ax.set_yticks([])
    ax.tick_params(labelsize=7)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    return fig


