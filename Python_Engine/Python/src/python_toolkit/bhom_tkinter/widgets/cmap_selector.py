"""Colormap selector widget with embedded matplotlib preview."""

from typing import Dict, List, Optional, Literal, Union
from tkinter import ttk
import tkinter as tk
import matplotlib as mpl
from matplotlib.colors import Colormap, ListedColormap
from python_toolkit.plot.cmap_sample import cmap_sample_plot
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

# Accepted colormap input types for colormaps parameter and set()/add_cmap()
CmapInput = Union[str, Colormap, List[str]]

class CmapSelector(BHoMBaseWidget):
    """A widget for selecting and previewing a matplotlib colormap.

    The ``colormaps`` parameter accepts a mixed list of three input types which
    may be freely combined:

    - ``str`` — a registered matplotlib colormap name (e.g. ``"viridis"``).
    - ``Colormap`` — any matplotlib ``Colormap``, ``ListedColormap`` or
      ``LinearSegmentedColormap`` object.
    - ``List[str]`` — a list of colour strings (hex codes or named colours)
      that is auto-converted to a ``ListedColormap``.

    All three types are fully backwards-compatible; existing code that passes
    only string names continues to work without any changes.
    """

    CATEGORICAL_CMAPS = [
        "Accent",
        "Dark2",
        "Paired",
        "Pastel1",
        "Pastel2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
    ]

    CONTINUOUS_CMAPS = [
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
        "turbo",
        "Blues",
        "Greens",
        "Greys",
        "Oranges",
        "Purples",
        "Reds",
        "YlGn",
        "YlGnBu",
        "YlOrBr",
        "YlOrRd",
        "coolwarm",
        "seismic",
        "Spectral",
        "RdYlBu",
        "RdYlGn",
        "twilight",
        "twilight_shifted",
        "hsv",
    ]

    def __init__(
        self,
        parent: ttk.Frame,
        colormaps: Optional[List[CmapInput]] = None,
        cmap_set: str = "all",
        cmap_bins: int = 256,
        default_cmap: Optional[CmapInput] = None,
        plot_size: tuple[int, int] = (400, 50),
        dropdown_position: Literal["n", "e", "s", "w"] = "n",
        **kwargs
    ) -> None:
        """
        Initialize the CmapSelector widget.

        Args:
            parent: Parent widget.
            colormaps: Optional list of colormaps to populate the selector.
                Each item may be a ``str`` name, a ``Colormap`` object, or a
                ``List[str]`` of colour strings.  When provided the preset
                ``cmap_set`` selection is ignored.
            cmap_set: Preset colormap set used when ``colormaps`` is ``None``.
                Allowed values: ``"all"``, ``"continuous"``, ``"categorical"``.
            cmap_bins: Number of discrete gradient bands in the preview swatch.
            default_cmap: Optional default colormap to pre-select.  Accepts
                the same input types as items in ``colormaps``.
            plot_size: ``(width, height)`` in pixels for the preview swatch.
            dropdown_position: Position of the dropdown relative to the
                preview swatch. ``"n"`` = above, ``"s"`` = below,
                ``"w"`` = left, ``"e"`` = right.
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)

        self.cmap_bins = cmap_bins
        self.plot_size = plot_size

        # Registry of custom (non-matplotlib-named) colormaps: label → Colormap
        self._custom_cmaps: Dict[str, Colormap] = {}

        # Create frame for cmap selection content
        self.cmap_frame = ttk.Frame(self.content_frame)
        self.cmap_frame.pack(side="top", fill="both", expand=True, anchor=self._pack_anchor)

        self.colormap_var = tk.StringVar(value="viridis")
        self._all_colormaps = self._get_all_colormaps()
        self._preset_map: Dict[str, List[str]] = {
            "all": self._all_colormaps,
            "continuous": self._filter_available(self.CONTINUOUS_CMAPS),
            "categorical": self._filter_available(self.CATEGORICAL_CMAPS),
        }
        self._uses_explicit_colormaps = colormaps is not None

        self.cmap_frame.columnconfigure(0, weight=1)
        self.cmap_frame.rowconfigure(0, weight=1)

        content = ttk.Frame(self.cmap_frame, width=plot_size[0], height=plot_size[1])
        content.grid(row=0, column=0, padx=0, pady=4, sticky=self._grid_sticky)
        content.grid_propagate(False)

        self.cmap_set_var = tk.StringVar(value=cmap_set.lower())

        pos = dropdown_position.lower()
        is_horizontal = pos in ("w", "e")
        pack_side_combo: Literal["left", "right", "top", "bottom"] = {"n": "top", "s": "bottom", "w": "left", "e": "right"}[pos]  # type: ignore[assignment]
        pack_side_figure: Literal["left", "right", "top", "bottom"] = {"n": "top", "s": "top", "w": "left", "e": "left"}[pos]  # type: ignore[assignment]

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
        self.cmap_combobox.pack(side=tk.TOP, anchor=self._pack_anchor, padx=0)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self._on_cmap_selected)

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

        # Resolve default_cmap: may itself be a Colormap object or colour list
        self._default_label = self._resolve_default_label(default_cmap, current_colormaps)
        self._select_default_cmap(current_colormaps)

    def _get_all_colormaps(self) -> List[str]:
        """Return all registered colormap names, including reversed variants.

        Returns:
            List[str]: Sorted list of available colormap names.
        """
        # Base names available in this matplotlib build
        base_names = set(mpl.colormaps())

        # Include reversed variants (name_r) next to each base map
        all_names = set(base_names)
        for name in list(base_names):
            if not name.endswith("_r"):
                all_names.add(f"{name}_r")

        return sorted(all_names)

    def _filter_available(self, names: List[str]) -> List[str]:
        """Filter a candidate list to names available in the current matplotlib build.

        Args:
            names: Candidate colormap names.

        Returns:
            List[str]: Candidate names available in the current environment.
        """
        available = set(self._all_colormaps)
        return [name for name in names if name in available]

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
        return self._with_reversed(self._preset_map.get(key, self._preset_map["all"]))

    def _resolve_colormaps(self, colormaps: List[CmapInput]) -> tuple[List[str], Dict[str, Colormap]]:
        """Normalise a mixed list of colormap inputs into display labels and a custom-cmap registry.

        Each item is handled as follows:

        - ``str``: treated as a named matplotlib colormap; silently skipped if
          not registered in the current build.
        - ``Colormap``: registered under ``cmap.name`` (or an auto-generated
          label when the name is empty or conflicts with an existing entry).
        - ``List[str]``: converted to a ``ListedColormap``; auto-labelled.

        Args:
            colormaps: Mixed list of colormap inputs.

        Returns:
            tuple[List[str], Dict[str, Colormap]]: Ordered display label list
                and a mapping of label → Colormap for non-standard entries.
        """
        display_names: List[str] = []
        custom_cmaps: Dict[str, Colormap] = {}
        list_counter = 0

        for item in colormaps:
            if isinstance(item, str):
                if item in self._all_colormaps and item not in display_names:
                    display_names.append(item)
            elif isinstance(item, Colormap):
                label = self._unique_label(item.name or "custom", display_names, custom_cmaps)
                display_names.append(label)
                custom_cmaps[label] = item
            elif isinstance(item, list):
                list_counter += 1
                try:
                    cmap = ListedColormap(item, name=f"custom_{list_counter}")
                    label = self._unique_label(cmap.name, display_names, custom_cmaps)
                    display_names.append(label)
                    custom_cmaps[label] = cmap
                except Exception:
                    pass  # Invalid colour strings - skip silently

        return display_names, custom_cmaps

    def _unique_label(self, candidate: str, existing: List[str], custom_map: Dict[str, Colormap]) -> str:
        """Return a label that is unique within ``existing`` and ``custom_map``.

        Args:
            candidate: Preferred label string.
            existing: Already-used display labels.
            custom_map: Already-registered custom colormap entries.

        Returns:
            str: Unique label derived from ``candidate``.
        """
        base = (candidate or "custom").strip() or "custom"
        label = base
        counter = 1
        while label in existing or label in custom_map:
            label = f"{base}_{counter}"
            counter += 1
        return label

    def _resolve_default_label(self, default: Optional[CmapInput], available: List[str]) -> Optional[str]:
        """Resolve a ``default_cmap`` value of any input type to a display label.

        Args:
            default: The raw ``default_cmap`` argument passed by the caller.
            available: Currently populated display label list.

        Returns:
            Optional[str]: Matching display label, or ``None`` when not found.
        """
        if default is None:
            return None
        if isinstance(default, str):
            return default if default in available else None
        if isinstance(default, Colormap):
            for label, cmap in self._custom_cmaps.items():
                if cmap is default:
                    return label
            return None
        if isinstance(default, list):
            for label, cmap in self._custom_cmaps.items():
                if isinstance(cmap, ListedColormap):
                    try:
                        if list(cmap.colors) == default:  # type: ignore[arg-type]
                            return label
                    except Exception:
                        pass
            return None
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

    def _update_cmap_sample(self, *args) -> None:
        """Update the colormap sample plot.

        Resolves the selected label to a ``Colormap`` object (for custom entries)
        or a name string (for registered matplotlib colormaps), then delegates
        to ``cmap_sample_plot``.

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

        Returns the ``Colormap`` object for custom entries or the name string
        for registered matplotlib colormaps.  Returns ``None`` when nothing
        is selected.

        Returns:
            Optional[Union[str, Colormap]]: Selected colormap or ``None``.
        """
        name = self.colormap_var.get()
        if not name:
            return None
        return self._custom_cmaps.get(name, name)

    def get(self) -> Optional[Union[str, Colormap]]:
        """Return the currently selected colormap.

        - For standard matplotlib colormaps: returns the name string (backwards
          compatible with existing callers).
        - For custom colormaps (objects or colour lists): returns the
          ``Colormap`` object so it can be passed directly to matplotlib.

        Returns:
            Optional[Union[str, Colormap]]: Selected colormap or ``None``.
        """
        return self.get_selected_cmap()

    def get_cmap(self) -> Optional[Colormap]:
        """Return the selected colormap always as a resolved ``Colormap`` object.

        Unlike ``get()``, this method resolves named matplotlib colormaps to
        their ``Colormap`` object, making it suitable for direct use in
        matplotlib calls regardless of input type.

        Returns:
            Optional[Colormap]: Resolved ``Colormap``, or ``None`` when empty.
        """
        name = self.colormap_var.get()
        if not name:
            return None
        if name in self._custom_cmaps:
            return self._custom_cmaps[name]
        try:
            return mpl.colormaps[name]
        except KeyError:
            return None

    def add_cmap(self, cmap: CmapInput, label: Optional[str] = None) -> Optional[str]:
        """Dynamically add a new colormap entry to the selector.

        The new entry is appended to the combobox and becomes immediately
        selectable.  If ``label`` is not provided, one is derived from
        ``cmap.name`` (for ``Colormap`` objects) or auto-generated.

        Args:
            cmap: Colormap to add.  May be a ``str`` name, ``Colormap``
                object, or ``List[str]`` of colour strings.
            label: Optional display label override.

        Returns:
            Optional[str]: The display label used for the new entry, or
                ``None`` if the input was invalid or already present.
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
            except Exception:
                return None
        else:
            return None

        final_label = self._unique_label(base, existing, self._custom_cmaps)
        self._custom_cmaps[final_label] = cmap
        existing.append(final_label)
        self._populate_cmap_list(existing)
        return final_label

    def set(self, value: Optional[CmapInput]) -> None:
        """Set the selected colormap.

        Accepts the same input types as ``colormaps`` list items:

        - ``str``: selects by name if present in the combobox.
        - ``Colormap``: selects the matching registered custom entry by object
          identity.
        - ``List[str]``: selects the matching ``ListedColormap`` entry by
          colour list equality.
        - ``None``: clears the selection.

        Args:
            value: Colormap to select, or ``None`` to clear.
        """
        if value is None:
            self.figure_widget.clear()
            self.colormap_var.set("")
            return

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
                        pass
            self.figure_widget.clear()
            self.colormap_var.set("")

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current colormap selection.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                ``(is_valid, message, severity)`` where severity is ``None``
                when valid, or ``"error"`` for an invalid selection.
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

    root.mainloop()

    # After mainloop — demonstrate get() vs get_cmap() return types
    print("selector_strings.get()   :", selector_strings.get())       # str
    print("selector_colours.get()   :", selector_colours.get())       # Colormap object
    print("selector_objects.get()   :", selector_objects.get())       # Colormap object
    print("selector_preset.get()    :", selector_preset.get())        # str
    print("selector_preset.get_cmap():", selector_preset.get_cmap()) # Colormap object