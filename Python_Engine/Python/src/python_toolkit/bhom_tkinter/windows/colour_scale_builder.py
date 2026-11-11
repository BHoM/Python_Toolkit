"""Window for building colour scales from the data they will colour.

Pass the data in and the window shows its distribution, suggests band thresholds, and
lets the user colour, label and save the scale to the saved scales file
(see ``python_toolkit.colour_scales``)::

    builder = ColourScaleBuilder(parent, data=room_temperatures, units="degC")
    builder.run()
    scale = builder.saved_scale  # None if closed without saving
"""

import math
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Callable, Iterable, Optional, Sequence

import numpy as np

from python_toolkit.bhom.logging import CONSOLE_LOGGER
from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow
from python_toolkit.bhom_tkinter.theming.scaling import scale as scale_px
from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions
from python_toolkit.bhom_tkinter.widgets.colour_picker import ColourPicker
from python_toolkit.bhom_tkinter.widgets.drop_down_selection import DropDownSelection
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets.label import Label
from python_toolkit.bhom_tkinter.widgets.spinbox import Spinbox
from python_toolkit.bhom_tkinter.widgets.validated_entry_box import ValidatedEntryBox
from python_toolkit.bhom_tkinter.windows.warning_box import WarningBox
from python_toolkit.colour_scales import (
    BreakMethod,
    ColourScale,
    ColourScaleError,
    finite_values,
    load_scales,
    save_scale,
    suggest_thresholds,
)
from python_toolkit.palettes import palette_names, sample_colours
from python_toolkit.plot.colour_scale_histogram import colour_scale_histogram

MAX_BANDS = 24
TYPING_DELAY = 700  # ms to wait after the last keystroke, so "22" is not read as "2" first
PLOT_WIDTH = 560  # the plot, the controls and the band table all share this width
ERROR_COLOUR = "#c0392b"

Bands = tuple[list[float], list[str], list[Optional[str]]]  # thresholds, colours, labels


@dataclass
class BandRow:
    """The widgets of one row of the band table."""

    colour: ColourPicker
    label: ValidatedEntryBox
    lower: ttk.Label
    upper: Optional[Spinbox]  # None for the last, open-ended band
    split: ttk.Button
    remove: ttk.Button


class ColourScaleBuilder(BHoMBaseChildWindow):
    """Build, preview and save a ColourScale against real data."""

    def __init__(
        self,
        parent: Optional[tk.Misc] = None,
        data: Optional[Iterable] = None,
        units: Optional[str] = None,
        scale: Optional[ColourScale] = None,
        library_path: Optional[Path] = None,
        on_save: Optional[Callable[[ColourScale], None]] = None,
        palette: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Args:
            parent: Owning window (None for a standalone window).
            data: Values the scale will colour; drives the histogram and suggestions.
            units: Units of the data, stored with the scale.
            scale: An existing scale to edit (saving replaces it).
            library_path: File to save into (defaults to the user's saved scales).
            on_save: Called with the saved scale.
            palette: Palette to start from (e.g. the plot's current one).
            **kwargs: Additional BHoMBaseChildWindow options.
        """
        self.values = finite_values(data)
        self.units = units if units is not None else (scale.units if scale else None)
        self.library_path = library_path
        self.editing = scale
        self.on_save = on_save
        self.saved_scale: Optional[ColourScale] = None
        self._band_rows: list[BandRow] = []
        self._preview_job: Optional[str] = None
        self._suggest_job: Optional[str] = None
        self._syncing = False
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
        """Lay out the name, data summary, preview, status line, controls and band table."""
        frame = self.content_frame
        frame.columnconfigure(0, weight=1)
        left = dict(column=0, sticky="ew", padx=0)

        self.name = _without_message_line(ValidatedEntryBox(
            frame, id="name", helper_text="Name", required=False, width=30,
            on_change=lambda _v: self._schedule_preview(TYPING_DELAY),  # re-checks, clearing old errors
            build_options=GridOptions(row=0, pady=3, **left)))
        self.data_text = Label(frame, text=self._data_summary(), build_options=GridOptions(row=2, **left))
        self.preview = FigureContainer(frame, id="preview", rigid_width=PLOT_WIDTH, rigid_height=130,
                                       build_options=GridOptions(row=3, pady=4, **left))
        self.status = Label(frame, text="", foreground=ERROR_COLOUR, wraplength=scale_px(PLOT_WIDTH), justify="left",
                            build_options=GridOptions(row=4, **left))
        self._build_controls(frame, row=5)

        self.bands_frame = ttk.Frame(frame)
        self.bands_frame.grid(row=6, pady=3, **left)
        self.bands_frame.columnconfigure(1, weight=1)  # the label box takes the spare width
        self.widgets = [self.name, self.data_text, self.preview, self.status]

    def _build_controls(self, parent: ttk.Frame, row: int) -> None:
        """Lay out the band count, break method and palette controls in one row."""
        controls = ttk.Frame(parent)
        controls.grid(row=row, column=0, sticky="ew", padx=0, pady=3)
        controls.columnconfigure(2, weight=1)  # the palette takes the spare width
        self.band_count = Spinbox(controls, id="bands", helper_text="Bands", values=list(range(2, MAX_BANDS + 1)),
                                  default=5, width=4, command=lambda _v: self._schedule_suggestion(TYPING_DELAY),
                                  build_options=GridOptions(row=0, column=0, sticky="w", padx=(0, 8)))
        self.method = DropDownSelection(controls, id="method", helper_text="Breaks",
                                        options=[method.value for method in BreakMethod],
                                        default=BreakMethod.NICE.value, state="readonly", width=7,
                                        command=lambda _v: self._schedule_suggestion(0),
                                        build_options=GridOptions(row=0, column=1, sticky="w", padx=(0, 8)))
        options = palette_names()
        self.palette = DropDownSelection(controls, id="palette", helper_text="Palette / colour map", options=options,
                                         default=self._start_palette if self._start_palette in options else "viridis",
                                         state="readonly", width=6, command=lambda _v: self._recolour(),
                                         build_options=GridOptions(row=0, column=2, sticky="ew"))
        for widget in (self.band_count, self.method, self.palette):
            widget.build()
        if not self.values.size:  # breaks are suggested from data; without it the thresholds are typed in
            self.band_count.spinbox.configure(state="disabled")
            self.method.combobox.configure(state="disabled")

    def _data_summary(self) -> str:
        """One line describing the data: count, range, median and middle half."""
        if not self.values.size:
            return "No data passed in: set the thresholds by hand."
        q1, median, q3 = np.quantile(self.values, [0.25, 0.5, 0.75])
        units = f" {self.units}" if self.units else ""
        return (f"{self.values.size} values from {self.values.min():.4g} to {self.values.max():.4g}{units}; "
                f"median {median:.4g}, middle half {q1:.4g} to {q3:.4g}")

    # ── state ──────────────────────────────────────────────────────────────

    def _load(self, scale: Optional[ColourScale]) -> None:
        """Fill the window from the scale being edited, or start a new one."""
        if scale is not None:
            self.name.set(scale.name)
            if isinstance(scale.cmap, str):
                self.palette.set(scale.cmap)
            self._show_bands(scale.thresholds, scale.colours(), scale.labels)
        else:
            self.name.set(self._unused_name("New scale"))
            if self.values.size:
                self._suggest()
            else:
                self._show_bands([1.0, 2.0], sample_colours(self.palette.get(), 3), None)
        self._schedule_preview()

    def _schedule_suggestion(self, delay: int) -> None:
        """Re-suggest the bands once the band count or break method has settled for `delay` ms."""
        if self._syncing or not self.values.size:
            return
        if self._suggest_job is not None:
            self.after_cancel(self._suggest_job)
        self._suggest_job = self.after(delay, self._run_scheduled_suggestion)

    def _run_scheduled_suggestion(self) -> None:
        """Suggest the bands, if the band count box holds a valid count."""
        self._suggest_job = None
        try:
            bands = int(self.band_count.get())
        except ValueError:  # half-typed count
            return
        if 2 <= bands <= MAX_BANDS:
            self._suggest()

    def _suggest(self) -> None:
        """Replace the thresholds with suggested ones, keeping hand-picked colours and labels where bands remain."""
        try:
            thresholds = suggest_thresholds(self.values, int(self.band_count.get()), self.method.get())
        except (ColourScaleError, ValueError) as error:
            self.status.set(str(error))
            return
        count = len(thresholds) + 1
        old_colours = [row.colour.get() for row in self._band_rows]
        old_labels = [(row.label.get() or "").strip() or None for row in self._band_rows]
        palette_colours = sample_colours(self.palette.get(), count)
        if old_colours and self._is_hand_coloured(old_colours):
            colours = [old_colours[i] if i < len(old_colours) else palette_colours[i] for i in range(count)]
        else:
            colours = palette_colours
        labels = (old_labels + [None] * count)[:count]
        self._show_bands(thresholds, colours, labels)

    def _split_band(self, index: int) -> None:
        """Add a band by splitting band `index` in two at the middle of its range; the new band starts unlabelled."""
        try:
            thresholds, colours, labels = self._read_bands()
        except ColourScaleError as error:
            self.status.set(str(error))
            return
        if len(colours) >= MAX_BANDS:
            return
        low, high = self._band_extent(index, thresholds)
        middle = float(f"{(low + high) / 2:.6g}")
        if not low < middle < high:
            self.status.set("There is no room to split this band; move its thresholds apart first.")
            return
        hand_coloured = self._is_hand_coloured(colours)
        thresholds.insert(index, middle)
        colours.insert(index + 1, colours[index])
        labels.insert(index + 1, None)
        self._show_edited_bands(thresholds, colours, labels, hand_coloured)

    def _band_extent(self, index: int, thresholds: Sequence[float]) -> tuple[float, float]:
        """The range of band `index`; an open end band runs to the data's extreme, or one typical band width."""
        count = len(thresholds) + 1
        typical = float(np.mean(np.diff(thresholds))) if len(thresholds) > 1 else 0.0
        if not typical and self.values.size:
            typical = float(self.values.max() - self.values.min()) / count
        typical = typical or 1.0
        lower = thresholds[index - 1] if index > 0 else None
        upper = thresholds[index] if index < count - 1 else None
        if lower is None:
            data_min = float(self.values.min()) if self.values.size else None
            lower = data_min if data_min is not None and data_min < upper else upper - typical
        if upper is None:
            data_max = float(self.values.max()) if self.values.size else None
            upper = data_max if data_max is not None and data_max > lower else lower + typical
        return lower, upper

    def _remove_band(self, index: int) -> None:
        """Remove band `index`; its range joins the band after it (before it, for the last band)."""
        try:
            thresholds, colours, labels = self._read_bands()
        except ColourScaleError as error:
            self.status.set(str(error))
            return
        count = len(colours)
        if count <= 2:
            return
        hand_coloured = self._is_hand_coloured(colours)
        thresholds.pop(min(index, count - 2))
        colours.pop(index)
        labels.pop(index)
        self._show_edited_bands(thresholds, colours, labels, hand_coloured)

    def _show_edited_bands(self, thresholds: list[float], colours: list[str], labels: list[Optional[str]],
                           hand_coloured: bool) -> None:
        """Show an edited band table: hand-picked colours stay, otherwise the palette is spread over the new bands."""
        if not hand_coloured:
            colours = sample_colours(self.palette.get(), len(colours))
        self._show_bands(thresholds, colours, labels)

    def _is_hand_coloured(self, colours: list[str]) -> bool:
        """Whether the band colours differ from the selected palette's, i.e. were picked by hand."""
        return colours != sample_colours(self.palette.get(), len(colours))

    def _recolour(self) -> None:
        """Recolour the bands from the newly selected palette, keeping their thresholds and labels."""
        if not self._band_rows:
            return
        for row, colour in zip(self._band_rows, sample_colours(self.palette.get(), len(self._band_rows))):
            row.colour.set(colour)
        self._schedule_preview()

    def _show_bands(self, thresholds: Sequence[float], colours: Sequence[str],
                    labels: Optional[Sequence[Optional[str]]]) -> None:
        """Rebuild the band table with one row per colour."""
        for child in self.bands_frame.winfo_children():
            child.destroy()
        for column, text in enumerate(("Colour", "Label (legend)", "From", "Up to", "")):
            ttk.Label(self.bands_frame, text=text, style="Caption.TLabel").grid(row=0, column=column, sticky="w",
                                                                              padx=(0, 8))
        labels = labels or [None] * len(colours)
        self._band_rows = [self._add_band_row(i, thresholds, colours[i], labels[i]) for i in range(len(colours))]
        self._syncing = True  # showing the count must not re-suggest the bands
        self.band_count.set(len(colours))
        self._syncing = False
        self._schedule_preview()
        if self._has_been_shown:  # the window follows the number of band rows
            self.update_idletasks()
            self._apply_sizing()

    def _add_band_row(self, index: int, thresholds: Sequence[float], colour: str, label: Optional[str]) -> BandRow:
        """Add the widgets for band `index` to the band table."""
        row = index + 1  # below the header
        count = len(thresholds) + 1
        picker = ColourPicker(self.bands_frame, default_colour=colour, swatch_width=36, swatch_height=20,
                              command=lambda _c: self._schedule_preview())
        picker.grid(row=row, column=0, sticky="w", padx=(0, 8))
        label_box = _without_message_line(ValidatedEntryBox(
            self.bands_frame, required=False, width=10, on_change=lambda _v: self._schedule_preview(TYPING_DELAY)))
        label_box.grid(row=row, column=1, sticky="ew", padx=(0, 8))
        label_box.set(label or "")
        lower = ttk.Label(self.bands_frame, text="")
        lower.grid(row=row, column=2, sticky="w", padx=(0, 8))
        upper = self._threshold_spinbox(thresholds, index) if index < count - 1 else None
        if upper is not None:
            upper.grid(row=row, column=3, sticky="w")
        else:
            ttk.Label(self.bands_frame, text="and above").grid(row=row, column=3, sticky="w")
        actions = ttk.Frame(self.bands_frame)
        actions.grid(row=row, column=4, sticky="e", padx=(8, 0))
        split = ttk.Button(actions, text="Split", width=6, command=lambda: self._split_band(index))
        remove = ttk.Button(actions, text="Remove", width=7, command=lambda: self._remove_band(index))
        split.pack(side="left", padx=(0, 4))
        remove.pack(side="left")
        if count >= MAX_BANDS:
            split.state(["disabled"])
        if count <= 2:
            remove.state(["disabled"])
        return BandRow(picker, label_box, lower, upper, split, remove)

    def _threshold_spinbox(self, thresholds: Sequence[float], index: int) -> Spinbox:
        """A spin box for threshold `index`, stepping about 1% of the data range, within one range either side."""
        known = [*thresholds, *([self.values.min(), self.values.max()] if self.values.size else [])]
        low, high = min(known), max(known)
        span = (high - low) or 1.0
        spinbox = Spinbox(self.bands_frame, from_=low - span, to=high + span, increment=_round_step(span), width=10,
                          command=lambda _v: self._schedule_preview(TYPING_DELAY))
        spinbox.spinbox.configure(format="%.6g")  # no float noise while spinning
        spinbox.set(f"{thresholds[index]:.6g}")
        return spinbox

    def _read_bands(self) -> Bands:
        """Read the band table.

        Returns:
            Bands: The thresholds, colours and labels (None where blank).

        Raises:
            ColourScaleError: If a threshold is not a number.
        """
        thresholds = []
        for i, row in enumerate(self._band_rows[:-1]):
            text = str(row.upper.get()).strip()
            try:
                thresholds.append(float(text))
            except ValueError:
                raise ColourScaleError(f"Band {i + 1}: '{text}' is not a number.") from None
        colours = [row.colour.get() for row in self._band_rows]
        labels = [(row.label.get() or "").strip() or None for row in self._band_rows]
        return thresholds, colours, labels

    def current_scale(self) -> ColourScale:
        """The scale the window describes right now.

        Returns:
            ColourScale: The scale. Its colours are the palette name unless a band colour was picked by hand.

        Raises:
            ColourScaleError: If the name, thresholds or colours are invalid.
        """
        thresholds, colours, labels = self._read_bands()
        cmap = colours if self._is_hand_coloured(colours) else self.palette.get()
        return ColourScale((self.name.get() or "").strip(), thresholds, cmap, labels if any(labels) else None,
                           self.units)

    def _unused_name(self, base: str) -> str:
        """`base`, or `base 2`, `base 3`... whichever is not yet a saved scale's name."""
        try:
            taken = {scale.name for scale in load_scales(self.library_path)}
        except ColourScaleError as error:  # an unreadable library must not stop the window opening; saving reports it
            CONSOLE_LOGGER.warning(str(error))
            taken = set()
        name, number = base, 1
        while name in taken:
            number += 1
            name = f"{base} {number}"
        return name

    def _save(self) -> None:
        """Save the scale to the library and close; errors are shown in a pop-up and the window stays open."""
        try:
            scale = self.current_scale()
            save_scale(scale, self.library_path, replaces=self.editing.name if self.editing else None)
        except (ColourScaleError, OSError) as error:
            self._show_save_error(str(error))
            return
        CONSOLE_LOGGER.info(f"Saved colour scale '{scale.name}'.")
        self.saved_scale = scale
        if self.on_save is not None:
            self.on_save(scale)
        self.destroy_root()

    def _show_save_error(self, message: str) -> None:
        """Show why the scale was not saved, in the status line and a pop-up."""
        if "already exists" in message:
            message += " Give this scale another name, or edit the saved one instead."
        self.status.set(message)
        box = WarningBox(title="Scale not saved", errors=[message], parent=self)
        box.build()
        box.run()

    # ── preview ────────────────────────────────────────────────────────────

    def _schedule_preview(self, delay: int = 250) -> None:
        """Redraw the preview once the window has been left unchanged for `delay` ms."""
        if self._preview_job is not None:
            try:
                self.after_cancel(self._preview_job)
            except tk.TclError:
                pass
        self._preview_job = self.after(delay, self._update_preview)

    def _update_preview(self) -> None:
        """Redraw the histogram and the band 'From' column, or report why the scale is invalid."""
        self._preview_job = None
        try:
            scale = self.current_scale()
        except ColourScaleError as error:
            self.status.set(str(error))
            return
        self.status.set("")
        for row, lower in zip(self._band_rows, [None, *scale.thresholds]):
            row.lower.configure(text="below" if lower is None else f"{lower:.6g}")
        style = ttk.Style()
        self.preview.embed_figure(colour_scale_histogram(
            scale, self.values,
            background=style.lookup("TFrame", "background") or "#ffffff",
            foreground=style.lookup("TLabel", "foreground") or "#000000"))


def _round_step(span: float) -> float:
    """A round step (1, 2 or 5 x 10^n) of about a hundredth of the span, for spinning a threshold."""
    raw = span / 100 if span > 0 else 0.01
    power = 10 ** math.floor(math.log10(raw))
    return next(factor * power for factor in (5, 2, 1) if factor * power <= raw)


def _without_message_line(box: ValidatedEntryBox) -> ValidatedEntryBox:
    """Drop the tick and the message line an entry box reserves, so its edges line up with its neighbours.

    Problems are reported in the window's status line instead."""
    box.success_label.pack_forget()
    box.error_label.pack_forget()
    return box


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
