"""Colormap selector widget with embedded matplotlib preview."""

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Literal, Union
from tkinter import messagebox, ttk
import tkinter as tk
import matplotlib as mpl
from matplotlib.colors import BoundaryNorm, Colormap, ListedColormap
from python_toolkit.plot.cmap_sample import cmap_sample_plot
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
from python_toolkit.plot import palettes
from python_toolkit.plot.colour_scales import ColourScale, ColourScaleError, clean_data, delete_scale, load_scales

from python_toolkit.bhom.analytics import CONSOLE_LOGGER
from python_toolkit.bhom_tkinter.theming.scaling import scale_pad

# Accepted colormap input types for colormaps parameter and set()/add_cmap()
CmapInput = Union[str, Colormap, List[str]]

class CmapSelector(BHoMBaseWidget):
    """A widget for selecting and previewing a matplotlib colormap.

    The `colormaps` parameter accepts a mixed list of three input types which
    may be freely combined:

    * `str`: a registered matplotlib `Colormap` name (e.g. "viridis").
    * `Colormap`: any matplotlib `Colormap`, `ListedColormap` or `LinearSegmentedColormap` object.
    * `List[str]`: a list of colour strings (hex codes or named colours) that is auto-converted to a `ListedColormap`.
    """

    def __init__(
        self,
        parent: ttk.Frame,
        colormaps: Optional[List[CmapInput]] = None,
        cmap_set: str = "all",
        cmap_bins: int = 256,
        default_cmap: Optional[CmapInput] = None,
        plot_size: tuple[int, int] = (400, 50),
        dropdown_position: Literal["n", "e", "s", "w"] = "n",
        include_scales: bool = False,
        data: Optional[Iterable] = None,
        units: Optional[str] = None,
        scales_path: Optional[Path] = None,
        **kwargs
    ) -> None:
        """
        Initialize the CmapSelector widget.

        Args:
            parent: Parent widget.
            colormaps: Optional list of colormaps to populate the selector.
                Each item may be a `str` name, a `Colormap` object, or a
                `List[str]` of colour strings.  When provided the preset
                `cmap_set` selection is ignored.
            cmap_set: Preset colormap set used when `colormaps` is `None`.
                Allowed values: "all", "continuous", "categorical", "colourblind"
                (see `python_toolkit.plot.palettes`).
            cmap_bins: Number of discrete gradient bands in the preview swatch.
            default_cmap: Optional default colormap to pre-select.  Accepts
                the same input types as items in `colormaps`.
            plot_size: `(width, height)` in pixels for the preview swatch.
            dropdown_position: Position of the dropdown relative to the
                preview swatch. "n" = above, "s" = below,
                "w" = left, "e" = right.
            include_scales: List the saved colour scales (see `python_toolkit.plot.colour_scales`)
                as "Name (scale)" entries, with buttons to build, edit and delete them.
                Use `get_scale()` and `get_norm()` to colour data with the selected scale.
            data: Values the scales will colour; passed to the scale builder for its
                histogram and break suggestions, and used to stretch the end bands.
            units: Units of `data`, stored with new scales.
            scales_path: Saved scales file (defaults to the user's saved scales).
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)

        self.cmap_bins = cmap_bins
        self.plot_size = plot_size
        self.include_scales = include_scales
        self.data = None if data is None else clean_data(data)
        self.units = units
        self.scales_path = scales_path
        self._scales: Dict[str, ColourScale] = {}  # combobox label -> saved scale

        # Registry of custom (non-matplotlib-named) colormaps: label → Colormap
        self._custom_cmaps: Dict[str, Colormap] = {}

        # Create frame for cmap selection content
        self.cmap_frame = ttk.Frame(self.content_frame)
        self.cmap_frame.pack(side="top", fill="both", expand=True, anchor=self._pack_anchor)

        self.colormap_var = tk.StringVar(value="viridis")
        self._all_colormaps = palettes.names()
        self._uses_explicit_colormaps = colormaps is not None

        self.cmap_frame.columnconfigure(0, weight=1)
        self.cmap_frame.rowconfigure(0, weight=1)

        content = ttk.Frame(self.cmap_frame, width=plot_size[0],
                            height=plot_size[1] + (scale_pad(34) if include_scales else 0))
        content.grid(row=0, column=0, padx=scale_pad(0), pady=scale_pad(4), sticky=self._grid_sticky)
        content.grid_propagate(False)

        self.cmap_set_var = tk.StringVar(value=cmap_set.lower())

        pos = dropdown_position.lower()
        is_horizontal = pos in ("w", "e")
        pack_side_combo = {"n": tk.TOP, "s": tk.BOTTOM, "w": tk.LEFT, "e": tk.RIGHT}[pos]  # type: ignore[assignment]
        pack_side_figure = {"n": tk.TOP, "s": tk.TOP, "w": tk.LEFT, "e": tk.LEFT}[pos]  # type: ignore[assignment]

        combo_padx = (0, 4) if is_horizontal else 0
        combo_pady = (8, 4) if not is_horizontal else 0

        header = ttk.Frame(content)
        header.pack(side=pack_side_combo, anchor=self._pack_anchor, padx=combo_padx, pady=combo_pady)

        self.cmap_combobox = ttk.Combobox(
            header,
            textvariable=self.colormap_var,
            state="readonly",
            justify=self._text_justify,
        )
        self.cmap_combobox.pack(side=tk.TOP, anchor=self._pack_anchor, padx=scale_pad(0))
        self.cmap_combobox.bind("<<ComboboxSelected>>", self._on_cmap_selected)
        if include_scales:
            self._build_scale_buttons(header)
            self.colormap_var.trace_add("write", lambda *_: self._update_scale_buttons())

        fill_mode: Literal["x", "y"] = "y" if is_horizontal else "x"
        self.figure_widget = FigureContainer(
            content,
            width=plot_size[0],
            height=plot_size[1],
            build_options=PackingOptions(side=pack_side_figure, anchor=self._pack_anchor, fill=fill_mode, padx=0, pady=(0, 8)),
        )
        self.figure_widget.build()

        if self._uses_explicit_colormaps:
            display_names, custom_cmaps = self._resolve_colormaps(colormaps or [])
            self._custom_cmaps.update(custom_cmaps)
            current_colormaps = display_names
        else:
            current_colormaps = self._preset_colormaps(self.cmap_set_var.get())

        self._populate_cmap_list(current_colormaps)
        if include_scales:
            self._refresh_scales()
            current_colormaps = list(self.cmap_combobox["values"])

        # Resolve default_cmap: may itself be a Colormap object or colour list
        self._default_label = self._resolve_default_label(default_cmap, current_colormaps)
        self._select_default_cmap(current_colormaps)

    def _with_reversed(self, names: List[str]) -> List[str]:
        """Return colormap names with reversed variants next to base maps.

        Args:
            names: Base colormap names.

        Returns:
            List[str]: Ordered list with available `_r` variants inserted.
        """
        available = set(self._all_colormaps)
        selected: List[str] = []
        for name in names:
            if name in available and name not in selected:
                selected.append(name)
            if not name.endswith("_r"):
                reversed_name = f"{name}_r"
                if reversed_name in available and reversed_name not in selected:
                    selected.append(reversed_name)
        return selected

    def _preset_colormaps(self, cmap_set: str) -> List[str]:
        """Resolve a preset colormap set name to a colormap list.

        Args:
            cmap_set: Preset set key.

        Returns:
            List[str]: Colormap names for the requested preset.
        """
        key = (cmap_set or "all").lower()
        return self._with_reversed(palettes.names(key if key in palettes.KINDS else None))

    def _resolve_colormaps(self, colormaps: List[CmapInput]) -> tuple[List[str], Dict[str, Colormap]]:
        """Normalise a mixed list of colormap inputs into display labels and a custom-cmap registry.

        Each item is handled as follows:

        * `str`: treated as a named matplotlib colormap
        * `Colormap`: registered under `cmap.name` (or an auto-generated label when the name is empty or conflicts with an existing entry).
        * `List[str]`: converted to a `ListedColormap`; auto-labelled.

        Args:
            colormaps: Mixed list of colormap inputs.

        Returns:
            tuple[List[str], Dict[str, Colormap]]: Ordered display label list and a mapping of label → Colormap for non-standard entries.
        """
        display_names: List[str] = []
        custom_cmaps: Dict[str, Colormap] = {}
        list_counter = 0

        for item in colormaps:
            if isinstance(item, str):
                if item in self._all_colormaps and item not in display_names:
                    display_names.append(item)
            elif isinstance(item, Colormap):
                label = self._unique_label(item.name or "custom", display_names)
                display_names.append(label)
                custom_cmaps[label] = item
            elif isinstance(item, list):
                list_counter += 1
                try:
                    cmap = ListedColormap(item, name=f"custom_{list_counter}")
                    label = self._unique_label(cmap.name, display_names)
                    display_names.append(label)
                    custom_cmaps[label] = cmap
                except Exception:
                    CONSOLE_LOGGER.warning(f"An error occurred when trying to convert a list of colours ({item}) to a `ListedColormap`. This cmap will not be available to select in UI.", exc_info=1)
                    pass

        return display_names, custom_cmaps

    def _unique_label(self, candidate: str, existing: List[str]) -> str:
        """Return a label that is unique within `existing`.

        Args:
            candidate: Preferred label string.
            existing: Already-used display labels.

        Returns:
            str: Unique label derived from `candidate`.
        """
        base = (candidate or "custom").strip() or "custom"
        label = base
        counter = 1
        while label in existing:
            label = f"{base}_{counter}"
            counter += 1
        return label

    def _resolve_default_label(self, default: Optional[CmapInput], available: List[str]) -> Optional[str]:
        """Resolve a `default_cmap` value of any input type to a display label.

        Args:
            default: The raw `default_cmap` argument passed by the caller.
            available: Currently populated display label list.

        Returns:
            Optional[str]: Matching display label, or `None` when not found.
        """
        if default is None:
            return None
        elif isinstance(default, str):
            return default if default in available else None
        elif isinstance(default, Colormap):
            for label, cmap in self._custom_cmaps.items():
                if cmap is default:
                    return label
        elif isinstance(default, list):
            for label, cmap in self._custom_cmaps.items():
                if isinstance(cmap, ListedColormap):
                    if list(cmap.colors) == default:  # type: ignore[arg-type]
                        return label

        return None

    def _populate_cmap_list(self, colormaps: List[str]) -> None:
        """Replace the combobox options with the provided colormap names."""
        self.cmap_combobox["values"] = tuple(colormaps)

    def _select_default_cmap(self, colormaps: List[str]) -> None:
        """Select an initial colormap and render its preview."""
        if not colormaps:
            self.figure_widget.clear()
            self.colormap_var.set("")
            return

        label = self._default_label if self._default_label in colormaps else colormaps[0]
        self.colormap_var.set(label)
        self._update_cmap_sample()

    def _on_cmap_selected(self, event=None) -> None:
        """Handle combobox selection changes."""
        self._update_cmap_sample()
        self._fire_on_change(self.get())

    def _update_cmap_sample(self, *args) -> None:
        """Update the colormap sample plot.

        Resolves the selected label to a `Colormap` object (for custom entries)
        or a name string (for registered matplotlib colormaps), then delegates
        to `cmap_sample_plot`.

        Args:
            *args: Unused callback arguments from Tk traces/events.
        """
        name = self.colormap_var.get()
        if not name:
            self.figure_widget.clear()
            return

        # Use the stored Colormap object for custom entries; fall back to the
        # name string for standard matplotlib colormaps.
        cmap: Union[str, Colormap] = self._custom_cmaps.get(name, name)
        fig = cmap_sample_plot(cmap, figsize=(self.plot_size[0] / 100, self.plot_size[1] / 100), bins=self.cmap_bins)
        self.figure_widget.embed_figure(fig)

    def get_selected_cmap(self) -> Optional[Union[str, Colormap]]:
        """Return the currently selected colormap.

        Returns the `Colormap` object for custom entries or the name string
        for registered matplotlib colormaps.  Returns `None` when nothing
        is selected.

        Returns:
            Optional[Union[str, Colormap]]: Selected colormap or `None`.
        """
        name = self.colormap_var.get()
        if not name:
            return None
        return self._custom_cmaps.get(name, name)

    def get(self) -> Optional[Union[str, Colormap]]:
        """Return the currently selected colormap.

        * For standard matplotlib colormaps: returns the name string (backwards
          compatible with existing callers).
        * For custom colormaps (objects or colour lists): returns the
          `Colormap` object so it can be passed directly to matplotlib.

        Returns:
            Optional[Union[str, Colormap]]: Selected colormap or `None`.
        """
        return self.get_selected_cmap()

    def get_cmap(self) -> Optional[Colormap]:
        """Return the selected colormap always as a resolved `Colormap` object.

        Unlike `get()`, this method resolves named matplotlib colormaps to
        their `Colormap` object, making it suitable for direct use in
        matplotlib calls regardless of input type.

        Returns:
            Optional[Colormap]: Resolved `Colormap`, or `None` when empty.
        """
        name = self.colormap_var.get()
        if not name:
            return None
        if name in self._custom_cmaps:
            return self._custom_cmaps[name]

        return mpl.colormaps.get(name)

    # ── saved colour scales ────────────────────────────────────────────────

    @staticmethod
    def _scale_label(name: str) -> str:
        return f"{name} (scale)"

    def _build_scale_buttons(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.pack(side=tk.TOP, anchor=self._pack_anchor, pady=(4, 0))
        self.new_scale_button = ttk.Button(row, text="New scale…", command=lambda: self._open_builder(None))
        self.edit_scale_button = ttk.Button(row, text="Edit…", command=self._edit_scale)
        self.delete_scale_button = ttk.Button(row, text="Delete", command=self._delete_scale)
        for button in (self.new_scale_button, self.edit_scale_button, self.delete_scale_button):
            button.pack(side=tk.LEFT, padx=(0, 4))
        self._update_scale_buttons()

    def _update_scale_buttons(self) -> None:
        state = ["!disabled"] if self.get_scale() is not None else ["disabled"]
        self.edit_scale_button.state(state)
        self.delete_scale_button.state(state)

    def _refresh_scales(self, select: Optional[str] = None) -> None:
        """Reload the saved scales into the dropdown, keeping the selection (or selecting the scale named `select`)."""
        previous = self.colormap_var.get()
        for label in self._scales:
            self._custom_cmaps.pop(label, None)
        try:
            scales = load_scales(self.scales_path)
        except ColourScaleError as e:  # an unreadable file must not break the selector
            CONSOLE_LOGGER.warning(str(e))
            scales = []
        palette_values = [v for v in self.cmap_combobox["values"] if v not in self._scales]
        self._scales = {self._scale_label(s.name): s for s in scales}
        for label, scale in self._scales.items():
            self._custom_cmaps[label] = scale.mapping(self.data)[0]
        self._populate_cmap_list(palette_values + list(self._scales))
        target = self._scale_label(select) if select else previous
        if target in self.cmap_combobox["values"]:
            self.colormap_var.set(target)
            self._update_cmap_sample()
        elif previous:  # the selected scale was deleted
            self.colormap_var.set(palette_values[0] if palette_values else "")
            self._update_cmap_sample()

    def _open_builder(self, scale: Optional[ColourScale]) -> None:
        """Open the scale builder to make a new scale, or edit `scale`; the saved scale is then selected."""
        # imported here: the window imports the widgets package, so a top-level import would be circular
        from python_toolkit.bhom_tkinter.windows.colour_scale_builder import ColourScaleBuilder

        current = self.colormap_var.get()
        builder = ColourScaleBuilder(
            self.winfo_toplevel(), data=self.data, units=self.units, scale=scale, library_path=self.scales_path,
            palette=current if current in palettes.names() else None, on_save=self._on_scale_saved)
        builder.run()

    def _on_scale_saved(self, scale: ColourScale) -> None:
        self._refresh_scales(select=scale.name)
        self._fire_on_change(self.get())

    def _edit_scale(self) -> None:
        scale = self.get_scale()
        if scale is not None:
            self._open_builder(scale)

    def _delete_scale(self) -> None:
        scale = self.get_scale()
        if scale is None or not messagebox.askyesno("Delete colour scale", f"Delete the saved scale '{scale.name}'?"):
            return
        try:
            delete_scale(scale.name, self.scales_path)
        except (ColourScaleError, OSError) as e:
            messagebox.showerror("Delete colour scale", str(e))
            return
        self._refresh_scales()
        self._fire_on_change(self.get())

    def get_scale(self) -> Optional[ColourScale]:
        """The selected saved colour scale, or None when a plain palette is selected."""
        return self._scales.get(self.colormap_var.get())

    def get_norm(self) -> Optional[BoundaryNorm]:
        """The normaliser for the selected scale (thresholds in data units), or None for a plain palette.

        Colour data with `get_cmap()` and `get_norm()` together; the end bands run to the `data` given."""
        scale = self.get_scale()
        return scale.mapping(self.data)[1] if scale is not None else None

    def add_cmap(self, cmap: CmapInput, label: Optional[str] = None) -> Optional[str]:
        """Dynamically add a new colormap entry to the selector.

        The new entry is appended to the combobox and becomes immediately
        selectable.  If `label` is not provided, one is derived from
        `cmap.name` (for `Colormap` objects) or auto-generated.

        Args:
            cmap: Colormap to add.  May be a `str` name, `Colormap`
                object, or `List[str]` of colour strings.
            label: Optional display label override.

        Returns:
            Optional[str]: The display label used for the new entry, or
                `None` if the input was invalid or already present.
        """
        existing = list(self.cmap_combobox["values"])

        if isinstance(cmap, str):
            if cmap not in self._all_colormaps or cmap in existing:
                return None
            existing.append(cmap)
            self._populate_cmap_list(existing)
            return cmap

        if isinstance(cmap, Colormap):
            base = label or cmap.name or "custom"
        elif isinstance(cmap, list):
            base = label or "custom"
            try:
                cmap = ListedColormap(cmap, name=base)
            except Exception: #currently these are warnings, but maybe they should be replaced with raised exceptions? ValueError here and TypeError for the fallback.
                CONSOLE_LOGGER.warning(f"List-like cmap ({cmap}) could not be added due to an error when converting to a `ListedColormap`.", exc_info=1)
                return None
        else:
            CONSOLE_LOGGER.warning(f"Input of type {type(cmap)} was not a valid type for cmap. Expected a str, list or matplotlib Colormap")
            return None

        final_label = self._unique_label(base, existing)
        self._custom_cmaps[final_label] = cmap
        existing.append(final_label)
        self._populate_cmap_list(existing)
        return final_label

    def set(self, value: Optional[CmapInput]) -> None:
        """Set the selected colormap.

        Accepts the same input types as `colormaps` list items:

        * `str`: selects by name if present in the combobox.
        * `Colormap`: selects the matching registered custom entry by object
          identity.
        * `List[str]`: selects the matching `ListedColormap` entry by
          colour list equality.
        * `None`: clears the selection.

        Args:
            value: Colormap to select, or `None` to clear.
        """
        if value is None:
            self.figure_widget.clear()
            self.colormap_var.set("")
            return

        if isinstance(value, ColourScale):
            value = self._scale_label(value.name)

        if isinstance(value, str):
            if value in self.cmap_combobox["values"]:
                self.colormap_var.set(value)
                self._update_cmap_sample()
            else:
                self.figure_widget.clear()
                self.colormap_var.set("")
            return

        if isinstance(value, Colormap):
            for label, cmap in self._custom_cmaps.items():
                if cmap is value:
                    self.colormap_var.set(label)
                    self._update_cmap_sample()
                    return
            self.figure_widget.clear()
            self.colormap_var.set("")
            return

        if isinstance(value, list):
            for label, cmap in self._custom_cmaps.items():
                if isinstance(cmap, ListedColormap):
                    try:
                        if list(cmap.colors) == value:  # type: ignore[arg-type]
                            self.colormap_var.set(label)
                            self._update_cmap_sample()
                            return
                    except Exception:
                        CONSOLE_LOGGER.debug("exception thrown when updating cmap sample from list value. visual cmap sample may be in invalid state?", exc_info=1)
                        pass
            self.figure_widget.clear()
            self.colormap_var.set("")

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current colormap selection.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None`
                when valid, or `"error"` for an invalid selection.
        """
        name = self.colormap_var.get()
        if not name:
            return self.apply_validation((False, "No colormap selected.", "error"))
        if name not in self.cmap_combobox["values"]:
            return self.apply_validation((False, f"Selected colormap '{name}' is not available.", "error"))
        return self.apply_validation((True, None, None))
            
if __name__ == "__main__":
    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from matplotlib.colors import LinearSegmentedColormap

    root = BHoMBaseWindow()
    parent_container = root.content_frame

    # Example 1 — Backwards-compatible: named strings only (existing behaviour)
    selector_strings = CmapSelector(
        parent_container,
        colormaps=["viridis", "plasma", "inferno"],
        default_cmap="plasma",
        item_title="1. Named strings",
        helper_text="Standard matplotlib colormap names.",
        build_options=PackingOptions(fill="both", expand=True),
        cmap_bins=64,
        plot_size=(400, 40),
    )
    selector_strings.build()

    # Example 2 — Colour lists auto-converted to ListedColormap
    bhom_blues = ["#cce5ff", "#66b2ff", "#0066cc", "#003d7a"]
    selector_colours = CmapSelector(
        parent_container,
        colormaps=[
            bhom_blues,                              # list of hex strings
            ["red", "orange", "yellow", "green"],   # list of named colours
            "tab10",                                 # mixed with a named cmap
        ],
        default_cmap=bhom_blues,
        item_title="2. Colour lists",
        helper_text="Lists of hex / named colours are auto-converted to ListedColormap.",
        build_options=PackingOptions(fill="both", expand=True),
        cmap_bins=4,
        plot_size=(400, 40),
    )
    selector_colours.build()

    # Example 3 — Colormap objects (ListedColormap / LinearSegmentedColormap)
    custom_listed = ListedColormap(["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"], name="bhom_cat4")
    custom_linear = LinearSegmentedColormap.from_list("warm_to_cool", ["#d73027", "#f46d43", "#abd9e9", "#4575b4"])
    selector_objects = CmapSelector(
        parent_container,
        colormaps=[
            custom_listed,   # ListedColormap object
            custom_linear,   # LinearSegmentedColormap object
            "coolwarm",      # standard cmap alongside custom ones
        ],
        default_cmap=custom_linear,
        item_title="3. Colormap objects",
        helper_text="Colormap objects are accepted directly alongside named strings.",
        build_options=PackingOptions(fill="both", expand=True),
        cmap_bins=64,
        plot_size=(400, 40),
    )
    selector_objects.build()

    # Example 4 — Preset set (no explicit colormaps list); get_cmap() demo
    selector_preset = CmapSelector(
        parent_container,
        cmap_set="categorical",
        item_title="4. Preset set + get_cmap()",
        helper_text="get() returns the name string; get_cmap() always returns a Colormap object.",
        build_options=PackingOptions(fill="both", expand=True),
        cmap_bins=12,
        plot_size=(400, 40),
    )
    selector_preset.build()

    # Example 5 — add_cmap() used after construction
    selector_dynamic = CmapSelector(
        parent_container,
        colormaps=["viridis"],
        item_title="5. Dynamic add_cmap()",
        helper_text="add_cmap() appends a new entry at runtime.",
        build_options=PackingOptions(fill="both", expand=True),
        cmap_bins=32,
        plot_size=(400, 40),
    )
    selector_dynamic.build()
    selector_dynamic.add_cmap(["#003366", "#0066cc", "#99ccff"], label="brand_blue")
    selector_dynamic.add_cmap(custom_listed)

    # Example 6 — saved colour scales: build, edit and delete scales from sample data
    import numpy as np
    import tempfile

    selector_scales = CmapSelector(
        parent_container,
        cmap_set="colourblind",
        include_scales=True,
        data=np.random.default_rng(1).normal(22, 3, 300),
        units="degC",
        scales_path=Path(tempfile.gettempdir()) / "cmap_selector_demo_scales.json",  # not your saved scales
        item_title="6. Colour scales",
        helper_text="New scale... opens the builder; saved scales appear as 'Name (scale)'.",
        build_options=PackingOptions(fill="both", expand=True),
        plot_size=(400, 40),
    )
    selector_scales.build()

    root.mainloop()

    # After mainloop — demonstrate get() vs get_cmap() return types
    print("selector_strings.get()   :", selector_strings.get())       # str
    print("selector_colours.get()   :", selector_colours.get())       # Colormap object
    print("selector_objects.get()   :", selector_objects.get())       # Colormap object
    print("selector_preset.get()    :", selector_preset.get())        # str
    print("selector_preset.get_cmap():", selector_preset.get_cmap()) # Colormap object