"""Window for building colour scales from the data they will colour.

Pass the data in and the window shows its distribution, suggests band thresholds, and
lets the user colour, label and save the scale to the saved scales file
(``python_toolkit.plot.colour_scales``)::

    builder = ColourScaleBuilder(parent, data=room_temperatures, units="degC")
    builder.run()
    scale = builder.saved_scale  # None if closed without saving
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Callable, Iterable, List, Optional

import numpy as np
from matplotlib.figure import Figure

from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow
from python_toolkit.bhom_tkinter.windows.warning_box import WarningBox
from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions
from python_toolkit.bhom_tkinter.widgets.colour_picker import ColourPicker
from python_toolkit.bhom_tkinter.widgets.drop_down_selection import DropDownSelection
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets.label import Label
from python_toolkit.bhom_tkinter.widgets.spinbox import Spinbox
from python_toolkit.bhom_tkinter.widgets.validated_entry_box import ValidatedEntryBox
from python_toolkit.bhom_tkinter.theming.scaling import scale as scale_px
from python_toolkit.plot import palettes
from python_toolkit.plot.colour_scales import (
    SUGGESTION_METHODS,
    ColourScale,
    ColourScaleError,
    clean_data,
    load_scales,
    save_scale,
    suggest_thresholds,
)

MAX_BANDS = 12
TYPING_DELAY = 700  # ms to wait after the last keystroke, so "22" is not read as "2" first
PLOT_WIDTH = 560  # the plot, the controls and the band table all share this width
ERROR_COLOUR = "#c0392b"


def _spin_step(span: float) -> float:
    """A round step (1, 2 or 5 x 10^n) of about a hundredth of the span, for spinning a threshold."""
    raw = span / 100 if span > 0 else 0.01
    power = 10 ** math.floor(math.log10(raw))
    return next(factor * power for factor in (5, 2, 1) if factor * power <= raw)


def _plain(box: ValidatedEntryBox) -> ValidatedEntryBox:
    """Drop the tick and the message line an entry box reserves, so its edges line up with its neighbours.

    Problems are reported in the window's status line instead."""
    box.success_label.pack_forget()
    box.error_label.pack_forget()
    return box


class ColourScaleBuilder(BHoMBaseChildWindow):
    """Build, preview and save a ColourScale against real data."""

    def __init__(
        self,
        parent=None,
        data: Optional[Iterable] = None,
        units: Optional[str] = None,
        scale: Optional[ColourScale] = None,
        library_path: Optional[Path] = None,
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
            library_path: File to save into (defaults to the user's saved scales).
            on_save: Called with the saved scale.
            palette: Palette or matplotlib colour map to start from (e.g. the plot's current one).
        """
        self.values = clean_data(data)
        self.units = units if units is not None else (scale.units if scale else None)
        self.library_path = library_path
        self.editing = scale
        self.on_save = on_save
        self.saved_scale: Optional[ColourScale] = None
        self._band_rows: List[dict] = []
        self._pending = None
        self._syncing = False
        self._suggest_job = None
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
            min_width=kwargs.pop("min_width", 400),
            min_height=kwargs.pop("min_height", 400),
            **kwargs,
        )
        self._build_contents()
        self.build()
        self._load(scale)
        self.update_idletasks()
        self._apply_sizing()  # the band rows were added after the window first sized itself

    # ── layout ─────────────────────────────────────────────────────────────

    def _build_contents(self) -> None:
        frame = self.content_frame
        frame.columnconfigure(0, weight=1)
        left = dict(column=0, sticky="ew", padx=0)

        self.name = _plain(ValidatedEntryBox(
            frame, id="name", helper_text="Name", required=False, width=30,
            on_change=lambda _v: self._schedule_preview(TYPING_DELAY),  # re-checks, clearing old errors
            build_options=GridOptions(row=0, pady=3, **left)))
        self.data_text = Label(frame, text=self._summary_text(), build_options=GridOptions(row=2, **left))
        self.preview = FigureContainer(frame, id="preview", rigid_width=PLOT_WIDTH, rigid_height=130,
                                       build_options=GridOptions(row=3, pady=4, **left))
        self.status = Label(frame, text="", foreground=ERROR_COLOUR, wraplength=scale_px(PLOT_WIDTH), justify="left",
                            build_options=GridOptions(row=4, **left))

        controls = ttk.Frame(frame)
        controls.grid(row=5, pady=3, **left)
        controls.columnconfigure(2, weight=1)  # the palette takes the spare width
        self.band_count = Spinbox(controls, id="bands", helper_text="Bands", values=list(range(2, MAX_BANDS + 1)),
                                  default=5, width=4, command=lambda _v: self._auto_suggest(TYPING_DELAY),
                                  build_options=GridOptions(row=0, column=0, sticky="w", padx=(0, 8)))
        self.method = DropDownSelection(controls, id="method", helper_text="Breaks", options=list(SUGGESTION_METHODS),
                                        default="nice", state="readonly", width=7,
                                        command=lambda _v: self._auto_suggest(0),
                                        build_options=GridOptions(row=0, column=1, sticky="w", padx=(0, 8)))
        options = palettes.names()
        self.palette = DropDownSelection(controls, id="palette", helper_text="Palette / colour map", options=options,
                                         default=self._start_palette if self._start_palette in options else "viridis",
                                         state="readonly", width=6, command=lambda _v: self._recolour(),
                                         build_options=GridOptions(row=0, column=2, sticky="ew"))
        for widget in (self.band_count, self.method, self.palette):
            widget.build()
        if not self.values.size:  # breaks are suggested from data; without it the thresholds are typed in
            self.band_count.spinbox.configure(state="disabled")
            self.method.combobox.configure(state="disabled")

        self.bands_frame = ttk.Frame(frame)
        self.bands_frame.grid(row=6, pady=3, **left)
        self.bands_frame.columnconfigure(1, weight=1)  # the label box takes the spare width
        self.widgets = [self.name, self.data_text, self.preview, self.status]

    def _summary_text(self) -> str:
        if not self.values.size:
            return "No data passed in: set the thresholds by hand."
        q1, q2, q3 = np.quantile(self.values, [0.25, 0.5, 0.75])
        units = f" {self.units}" if self.units else ""
        return (f"{self.values.size} values from {self.values.min():.4g} to {self.values.max():.4g}{units}; "
                f"median {q2:.4g}, middle half {q1:.4g} to {q3:.4g}")

    # ── state ──────────────────────────────────────────────────────────────

    def _load(self, scale: Optional[ColourScale]) -> None:
        if scale is not None:
            self.name.set(scale.name)
            if isinstance(scale.cmap, str):
                self.palette.set(scale.cmap)
            self._set_bands(scale.thresholds, scale.colours(), scale.labels)
        elif self.values.size:
            self.name.set(self._unused_name("New scale"))
            self._suggest()
        else:
            self.name.set(self._unused_name("New scale"))
            self._set_bands([1.0, 2.0], palettes.sample(self.palette.get(), 3), None)
        self._schedule_preview()

    def _auto_suggest(self, delay: int) -> None:
        """Re-suggest the bands once the band count or break method has settled."""
        if self._syncing or not self.values.size:
            return
        if self._suggest_job is not None:
            self.after_cancel(self._suggest_job)
        self._suggest_job = self.after(delay, self._run_auto_suggest)

    def _run_auto_suggest(self) -> None:
        self._suggest_job = None
        try:
            bands = int(self.band_count.get())
        except ValueError:  # half-typed count
            return
        if 2 <= bands <= MAX_BANDS:
            self._suggest()

    def _suggest(self) -> None:
        try:
            bands = int(self.band_count.get())
            thresholds = suggest_thresholds(self.values, bands, self.method.get())
        except (ColourScaleError, ValueError) as e:
            self.status.set(str(e))
            return
        n = len(thresholds) + 1
        palette = self.palette.get()
        old_colours = [row["colour"].get() for row in self._band_rows]
        old_labels = [(row["label"].get() or "").strip() or None for row in self._band_rows]
        fresh = palettes.sample(palette, n)
        # keep hand-picked colours and any labels on the bands that remain; new breaks only replace the thresholds
        customised = bool(old_colours) and old_colours != palettes.sample(palette, len(old_colours))
        colours = [old_colours[i] if customised and i < len(old_colours) else fresh[i] for i in range(n)]
        labels = (old_labels + [None] * n)[:n]
        self._set_bands(thresholds, colours, labels if any(labels) else None)

    def _split_band(self, index: int) -> None:
        """Add a band by splitting this one in two at the middle of its range; the new band starts empty."""
        try:
            thresholds, colours, labels = self._read_bands()
        except ColourScaleError as e:
            self.status.set(str(e))
            return
        n = len(colours)
        if n >= MAX_BANDS:
            return
        typical = float(np.mean(np.diff(thresholds))) if len(thresholds) > 1 else 0.0
        if not typical and self.values.size:
            typical = float(self.values.max() - self.values.min()) / n
        typical = typical or 1.0
        lower = thresholds[index - 1] if index > 0 else None
        upper = thresholds[index] if index < n - 1 else None
        data_lo = float(self.values.min()) if self.values.size else None
        data_hi = float(self.values.max()) if self.values.size else None
        # an open end is split against the data's extreme, or one typical band width beyond the last threshold
        lo = lower if lower is not None else (data_lo if data_lo is not None and data_lo < upper else upper - typical)
        hi = upper if upper is not None else (data_hi if data_hi is not None and data_hi > lower else lower + typical)
        new = float(f"{(lo + hi) / 2:.6g}")
        if not lo < new < hi:
            self.status.set("There is no room to split this band; move its thresholds apart first.")
            return
        was_customised = colours != palettes.sample(self.palette.get(), n)
        thresholds.insert(index, new)
        colours.insert(index + 1, colours[index])
        labels.insert(index + 1, None)
        self._rebuild(thresholds, colours, labels, was_customised)

    def _remove_band(self, index: int) -> None:
        """Remove a band; its range joins the band after it (before it, for the last band)."""
        try:
            thresholds, colours, labels = self._read_bands()
        except ColourScaleError as e:
            self.status.set(str(e))
            return
        n = len(colours)
        if n <= 2:
            return
        was_customised = colours != palettes.sample(self.palette.get(), n)
        thresholds.pop(index if index < n - 1 else n - 2)
        colours.pop(index)
        labels.pop(index)
        self._rebuild(thresholds, colours, labels, was_customised)

    def _rebuild(self, thresholds, colours, labels, was_customised: bool) -> None:
        """Show an edited table: hand-picked colours stay, otherwise the palette is spread over the new bands."""
        if not was_customised:
            colours = palettes.sample(self.palette.get(), len(colours))
        self._set_bands(thresholds, colours, labels if any(labels) else None)

    def _recolour(self) -> None:
        """A new palette recolours the bands, keeping their thresholds and labels."""
        if not self._band_rows:
            return
        for row, colour in zip(self._band_rows, palettes.sample(self.palette.get(), len(self._band_rows))):
            row["colour"].set(colour)
        self._schedule_preview()

    def _set_bands(self, thresholds, colours, labels) -> None:
        for child in self.bands_frame.winfo_children():
            child.destroy()
        self._band_rows = []
        n = len(colours)
        # thresholds are spin boxes: step about 1% of the data range, anywhere from one range below to one above
        lo = min([*thresholds, *([self.values.min()] if self.values.size else [])])
        hi = max([*thresholds, *([self.values.max()] if self.values.size else [])])
        span = (hi - lo) or 1.0
        step = _spin_step(span)
        headers = ("Colour", "Label (legend)", "From", "Up to", "")
        for col, text in enumerate(headers):
            ttk.Label(self.bands_frame, text=text, style="Caption.TLabel").grid(row=0, column=col, sticky="w", padx=(0, 8))
        for i in range(n):
            picker = ColourPicker(self.bands_frame, default_colour=colours[i], swatch_width=36, swatch_height=20,
                                  command=lambda _c: self._schedule_preview())
            picker.grid(row=i + 1, column=0, sticky="w", padx=(0, 8))
            label = _plain(ValidatedEntryBox(self.bands_frame, required=False, width=10,
                                             on_change=lambda _v: self._schedule_preview(TYPING_DELAY)))
            label.grid(row=i + 1, column=1, sticky="ew", padx=(0, 8))
            label.set((labels[i] or "") if labels else "")
            lower = ttk.Label(self.bands_frame, text="")
            lower.grid(row=i + 1, column=2, sticky="w", padx=(0, 8))
            upper = None
            if i < n - 1:
                upper = Spinbox(self.bands_frame, from_=lo - span, to=hi + span, increment=step, width=10,
                                command=lambda _v: self._schedule_preview(TYPING_DELAY))
                upper.spinbox.configure(format="%.6g")  # no float noise while spinning
                upper.grid(row=i + 1, column=3, sticky="w")
                upper.set(f"{thresholds[i]:.6g}")
            else:
                ttk.Label(self.bands_frame, text="and above").grid(row=i + 1, column=3, sticky="w")
            actions = ttk.Frame(self.bands_frame)
            actions.grid(row=i + 1, column=4, sticky="e", padx=(8, 0))
            split = ttk.Button(actions, text="Split", width=6, command=lambda i=i: self._split_band(i))
            remove = ttk.Button(actions, text="Remove", width=7, command=lambda i=i: self._remove_band(i))
            split.pack(side="left", padx=(0, 4))
            remove.pack(side="left")
            if n >= MAX_BANDS:
                split.state(["disabled"])
            if n <= 2:
                remove.state(["disabled"])
            self._band_rows.append({"colour": picker, "label": label, "lower": lower, "upper": upper,
                                    "split": split, "remove": remove})
        self._syncing = True  # showing the count must not re-suggest the bands
        self.band_count.set(n)
        self._syncing = False
        self._schedule_preview()
        if self._has_been_shown:  # the window follows the number of band rows
            self.update_idletasks()
            self._apply_sizing()

    def _read_bands(self):
        """The table as (thresholds, colours, labels); raises ColourScaleError for a threshold that is not a number."""
        thresholds = []
        for i, row in enumerate(self._band_rows[:-1]):
            text = str(row["upper"].get()).strip()
            try:
                thresholds.append(float(text))
            except ValueError:
                raise ColourScaleError(f"Band {i + 1}: '{text}' is not a number.") from None
        colours = [row["colour"].get() for row in self._band_rows]
        labels = [(row["label"].get() or "").strip() or None for row in self._band_rows]
        return thresholds, colours, labels

    def current_scale(self) -> ColourScale:
        """The scale described by the window right now (raises ColourScaleError if invalid)."""
        name = (self.name.get() or "").strip()
        palette = self.palette.get()
        thresholds, colours, labels = self._read_bands()
        # keep the palette as the scale's colours unless a band colour was changed by hand
        cmap = palette if colours == palettes.sample(palette, len(colours)) else colours
        return ColourScale(name, thresholds, cmap, labels if any(labels) else None, self.units)

    def _unused_name(self, base: str) -> str:
        names = {s.name for s in load_scales(self.library_path)}
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
            save_scale(scale, self.library_path, overwrite=self.editing is not None and self.editing.name == scale.name)
        except (ColourScaleError, OSError) as e:
            message = str(e)
            if "already exists" in message:
                message += " Give this scale another name, or edit the saved one instead."
            self.status.set(message)
            box = WarningBox(title="Scale not saved", errors=[message], parent=self)
            box.build()
            box.run()
            return
        CONSOLE_LOGGER.info(f"Saved colour scale '{scale.name}'.")
        self.saved_scale = scale
        if self.on_save is not None:
            self.on_save(scale)
        self.destroy_root()

    # ── preview ────────────────────────────────────────────────────────────

    def _schedule_preview(self, delay: int = 250) -> None:
        if self._pending is not None:
            try:
                self.after_cancel(self._pending)
            except tk.TclError:
                pass
        self._pending = self.after(delay, self._update_preview)

    def _update_preview(self) -> None:
        self._pending = None
        try:
            scale = self.current_scale()
        except ColourScaleError as e:
            self.status.set(str(e))
            return
        self.status.set("")
        for row, lower in zip(self._band_rows, [None] + scale.thresholds):
            row["lower"].configure(text="below" if lower is None else f"{lower:.6g}")
        style = ttk.Style()
        self.preview.embed_figure(preview_figure(scale, self.values,
                                                 background=style.lookup("TFrame", "background") or "#ffffff",
                                                 foreground=style.lookup("TLabel", "foreground") or "#000000"))


def preview_figure(scale: ColourScale, values: np.ndarray, background: str = "#ffffff",
                   foreground: str = "#000000") -> Figure:
    """Histogram of the data over the scale's colours (or the colours alone without data).

    `background` and `foreground` are the window's colours, so the plot sits in light or dark mode.
    """
    fig = Figure(figsize=(5.6, 1.3), dpi=100, facecolor=background)
    ax = fig.add_axes([0.0, 0.2, 1.0, 0.76], facecolor=background)
    cmap, norm = scale.mapping()
    lo, hi = scale.value_range(values)
    xs = np.linspace(lo, hi, 400)
    ax.imshow(cmap(norm(xs))[np.newaxis, :, :], aspect="auto", extent=(xs[0], xs[-1], 0, 1), alpha=0.85,
              origin="lower", zorder=0)
    if values.size:
        counts, edges = np.histogram(values, bins=30, range=(lo, hi))
        ax.bar(edges[:-1], counts / max(counts.max(), 1), width=np.diff(edges), align="edge", color=foreground,
               alpha=0.45, edgecolor=background, linewidth=0.6, zorder=1)
    for t in scale.thresholds:
        if xs[0] <= t <= xs[-1]:
            ax.axvline(t, color=foreground, linewidth=1.2, zorder=2)
    ax.set_xlim(xs[0], xs[-1])
    ax.set_ylim(0, 1.05)
    ax.set_yticks([])
    ax.tick_params(labelsize=7, colors=foreground)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(foreground)
    return fig


if __name__ == "__main__":
    import tempfile

    # Build a colour scale from sample data; saved to a temp file so your own saved scales are untouched.
    temperatures = np.random.default_rng(1).normal(22, 3, 300)
    builder = ColourScaleBuilder(
        data=temperatures,
        units="degC",
        palette="okabe_ito",
        library_path=Path(tempfile.gettempdir()) / "colour_scale_builder_demo.json",
        on_save=lambda scale: print(f"Saved: {scale!r}"),
    )
    builder.run()
    print(builder.saved_scale)
