import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Iterable, List, Optional

from python_toolkit.bhom_tkinter.widgets.ListBox import ScrollableListBox
from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

class DirectoryFileSelector(BHoMBaseWindow):

    def __init__(
        self,
        directory: Path,
        file_types: Iterable[str],
        selection_label: str = "file(s)",
        **kwargs,
    ) -> None:
        self.directory = Path(directory)
        self.file_types = self._normalise_file_types(file_types)
        self.selection_label = selection_label
        self._cancelled = False
        self.selected_files: List[Path] = []

        self.files = self._discover_files()
        self.display_items = [self._display_value(file) for file in self.files]
        self.file_lookup = dict(zip(self.display_items, self.files))
        self.file_selector_listbox: Optional[ScrollableListBox] = None

        kwargs.setdefault("title", f"Select {selection_label}")
        kwargs.setdefault("min_width", 600)
        kwargs.setdefault("min_height", 400)
        kwargs.setdefault("submit_text", "OK")
        kwargs.setdefault("submit_command", self._on_submit)
        kwargs.setdefault("close_text", "Cancel")
        kwargs.setdefault("close_command", self._on_cancel)
        kwargs.setdefault("on_close_window", self._on_cancel)

        super().__init__(**kwargs)

    def build(self):
        ttk.Label(
            self.content_frame,
            text=f"Select the {self.selection_label} to analyse.",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 10))

        if self.file_selector_listbox is None:
            self.file_selector_listbox = ScrollableListBox(
                id="file_selector_listbox",
                parent=self.content_frame,
                items=self.display_items,
                selectmode=tk.MULTIPLE,
                height=12,
                show_selection_controls=True,
                packing_options=PackingOptions(fill='both', expand=True),
            )
            self.widgets.append(self.file_selector_listbox)

        super().build()

    def _normalise_file_types(self, file_types: Iterable[str]) -> List[str]:
        normalised = []
        for file_type in file_types:
            suffix = str(file_type).strip()
            if not suffix:
                continue
            if not suffix.startswith("."):
                suffix = f".{suffix}"
            normalised.append(suffix.lower())
        return normalised

    def _discover_files(self) -> List[Path]:
        if not self.directory.exists():
            return []

        matches = []
        for path in self.directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.file_types:
                matches.append(path)
        return sorted(matches)

    def _display_value(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.directory))
        except ValueError:
            return str(path)

    def _on_submit(self):
        """Handle OK button - capture selection before window closes."""
        selected = self.file_selector_listbox.get_selection() if self.file_selector_listbox else []
        self.selected_files = [self.file_lookup[item] for item in selected if item in self.file_lookup]
        self.destroy_root()

    def _on_cancel(self):
        """Handle Cancel button or window close."""
        self._cancelled = True
        self.destroy_root()

if __name__ == "__main__":
    # Example usage
    selector = DirectoryFileSelector(
        directory=Path.home(),
        file_types=[".py", ".txt"],
        selection_label="scripts and text files",
    )

    selector.mainloop()
    for file in selector.selected_files:
        print(file)