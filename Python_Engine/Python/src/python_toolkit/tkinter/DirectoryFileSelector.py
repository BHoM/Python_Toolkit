import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Iterable, List

from widgets.ListBox import ScrollableListBox
from DefaultRoot import DefaultRoot

class DirectoryFileSelector:
    def __init__(self, directory: Path, file_types: Iterable[str], selection_label: str = "file(s)") -> None:
        self.directory = Path(directory)
        self.file_types = self._normalise_file_types(file_types)
        self.selection_label = selection_label
        self._cancelled = False
        self._selected_files = []

        # Create DefaultRoot window
        self.window = DefaultRoot(
            title=f"Select {selection_label}",
            min_width=600,
            min_height=400,
            show_submit=True,
            submit_text="OK",
            submit_command=self._on_submit,
            show_close=True,
            close_text="Cancel",
            close_command=self._on_cancel,
            on_close_window=self._on_cancel,
        )

        self.files = self._discover_files()
        self.display_items = [self._display_value(file) for file in self.files]
        self.file_lookup = dict(zip(self.display_items, self.files))

        # Add content to the window's content frame
        ttk.Label(
            self.window.content_frame,
            text=f"Select the {self.selection_label} to analyse.",
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(0, 10))

        self.listbox = ScrollableListBox(
            self.window.content_frame,
            items=self.display_items,
            selectmode=tk.MULTIPLE,
            height=12,
            show_selection_controls=True,
        )
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.select_all()

        # Refresh sizing after adding widgets
        self.window.refresh_sizing()

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

    def run(self) -> List[Path]:
        result = self.window.run()
        if self._cancelled or result != "submit":
            return []
        return self._selected_files

    def _on_submit(self):
        """Handle OK button - capture selection before window closes."""
        selected = self.listbox.get_selection()
        self._selected_files = [self.file_lookup[item] for item in selected if item in self.file_lookup]

    def _on_cancel(self):
        """Handle Cancel button or window close."""
        self._cancelled = True


if __name__ == "__main__":
    # Example usage
    selector = DirectoryFileSelector(
        directory=Path.cwd(),
        file_types=[".py", ".txt"],
        selection_label="scripts and text files",
    )
    selected_files = selector.run()
    print("Selected files:")
    for file in selected_files:
        print(file)