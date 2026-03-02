"""Colormap selector widget with embedded matplotlib preview."""

from typing import Dict, List, Optional, Literal
from tkinter import ttk
import tkinter as tk
import matplotlib as mpl
from python_toolkit.plot.cmap_sample import cmap_sample_plot
from python_toolkit.bhom_tkinter.widgets.figure_container import FigureContainer
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

class CmapSelector(BHoMBaseWidget):
    """
    A widget for selecting and previewing a matplotlib colormap.
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
        colormaps: Optional[List[str]] = None,
        cmap_set: str = "all",
        cmap_bins: int = 256,
        default_cmap: Optional[str] = None,
        plot_size: tuple[int, int] = (400, 50),
        **kwargs
    ) -> None:
        """
        Initialize the CmapSelector widget.

        Args:
            parent: Parent widget
            colormaps: Optional explicit list of colormap names to include.
                If provided, preset set selection is disabled.
            cmap_set: Preset colormap set to use when colormaps is None.
                Allowed values: "all", "continuous", "categorical".
            default_cmap: Optional default colormap to select.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        #set custom cmap args 
        self.cmap_bins = cmap_bins
        self.default_cmap = default_cmap
        self.plot_size = plot_size

        # Create frame for cmap selection content
        self.cmap_frame = ttk.Frame(self.content_frame)
        self.cmap_frame.pack(side="top", fill="both", expand=True)

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
        content.grid(row=0, column=0, padx=4, pady=4)
        content.grid_propagate(False)

        header = ttk.Frame(content)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.cmap_set_var = tk.StringVar(value=cmap_set.lower())

        self.cmap_combobox = ttk.Combobox(
            header,
            textvariable=self.colormap_var,
            state="readonly",
        )
        self.cmap_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.cmap_combobox.bind("<<ComboboxSelected>>", self._on_cmap_selected)

        self.figure_widget = FigureContainer(
            content,
            width=plot_size[0],
            height=plot_size[1],
            build_options=PackingOptions(anchor="w", padx=8, pady=(0, 8)),
        )
        self.figure_widget.build()

        if self._uses_explicit_colormaps:
            current_colormaps = self._with_reversed(self._filter_available(colormaps or []))
        else:
            current_colormaps = self._preset_colormaps(self.cmap_set_var.get())

        self._populate_cmap_list(current_colormaps)
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

    def _populate_cmap_list(self, colormaps: List[str]) -> None:
        """Replace the combobox options with the provided colormap names."""
        self.cmap_combobox["values"] = tuple(colormaps)

    def _select_default_cmap(self, colormaps: List[str]) -> None:
        """Select an initial colormap and render its preview."""
        if not colormaps:
            self.figure_widget.clear()
            self.colormap_var.set("")
            return
        
        self.colormap_var.set(self.default_cmap if self.default_cmap in colormaps else colormaps[0])
        self._update_cmap_sample()

    def _on_cmap_selected(self, event=None) -> None:
        """Handle combobox selection changes."""
        self._update_cmap_sample()

    def _update_cmap_sample(self, *args) -> None:
        """Update the colormap sample plot.

        Args:
            *args: Unused callback arguments from Tk traces/events.
        """
        cmap_name = self.colormap_var.get()
        if not cmap_name:
            self.figure_widget.clear()
            return

        fig = cmap_sample_plot(cmap_name, figsize=(self.plot_size[0]/100, self.plot_size[1]/100), bins = self.cmap_bins)
        self.figure_widget.embed_figure(fig)

    def get_selected_cmap(self) -> Optional[str]:
        """Return the currently selected colormap name, or `None` if empty.

        Returns:
            Optional[str]: Current colormap name.
        """
        cmap_name = self.colormap_var.get()
        return cmap_name if cmap_name else None

    def get(self) -> Optional[str]:
        """Get the currently selected colormap name.

        Returns:
            Optional[str]: Current colormap name.
        """
        return self.get_selected_cmap()
    
    def set(self, value: Optional[str]):
        """Set the selected colormap by name.

        Args:
            value: Colormap name to select. Clears selection when invalid.
        """
        if value and value in self.cmap_combobox["values"]:
            self.colormap_var.set(value)
            self._update_cmap_sample()
        else:
            self.figure_widget.clear()
            self.colormap_var.set("")

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current colormap selection.
        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for an invalid selection.
        """
        selected_cmap = self.get_selected_cmap()
        if selected_cmap is None:
            return self.apply_validation((False, "No colormap selected.", "error"))
        if selected_cmap not in self.cmap_combobox["values"]:
            return self.apply_validation((False, f"Selected colormap '{selected_cmap}' is not available.", "error"))
        return self.apply_validation((True, None, None))
            
if __name__ == "__main__":
    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    root = BHoMBaseWindow()
    parent_container = root.content_frame

    cmap_selector = CmapSelector(
        parent_container, 
        cmap_set="all", 
        item_title="Colormap Selector", 
        helper_text="Select a colormap from the list.",
        build_options=PackingOptions(fill='both', expand=True),
        cmap_bins=6,
        plot_size=(400, 50),
    )

    cmap_selector_2 = CmapSelector(
        parent_container, 
        cmap_set="categorical", 
        item_title="Categorical Colormap Selector", 
        helper_text="Select a categorical colormap from the list.",
        build_options=PackingOptions(fill='both', expand=True),
        cmap_bins=6,
        plot_size=(50, 25),
    )



    cmap_selector.build()
    cmap_selector_2.build()

    root.mainloop()