"""Path selection widget for file or directory browsing."""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from typing import Optional, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button

class PathSelector(BHoMBaseWidget):
    """A reusable path/file selector widget with a button and a readonly entry."""

    def __init__(
            self, 
            parent: ttk.Frame,
            button_text="Browse...", 
            filetypes=None, 
            command=None, 
            initialdir=None, 
            entry_width=40,
            button_width=25,
            mode="file", 
            **kwargs):
        """
        Args:
            parent (tk.Widget): The parent widget.
            button_text (str): The text to display on the button.
            filetypes (list, optional): List of filetypes for the dialog.
            command (callable, optional): Called with the file path after selection.
            initialdir (str, optional): Initial directory for the file dialog.
            mode (str): Either "file" or "directory" to select files or directories.
            item_title (str, optional): Optional header text shown at the top of the widget frame.
            helper_text (str, optional): Optional helper text shown above the entry box.
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)
        self.path_var = tk.StringVar()
        self.command = command
        self.mode = mode
        self.initialdir = initialdir
        self.filetypes = filetypes if filetypes is not None else [("All Files", "*.*")]
        self.display_name = tk.StringVar()
        self.entry = ttk.Entry(self.content_frame, textvariable=self.display_name, width=entry_width)
        self.entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        # Use Button wrapper but expose inner ttk.Button for backward compatibility
        button_widget = Button(self.content_frame, text=button_text, command=self._on_click, width=button_width)
        button_widget.pack(side=tk.LEFT)
        self.button = button_widget.button

    def _on_click(self):
        if self.mode == "directory":
            path = filedialog.askdirectory(
                initialdir=self.initialdir
            )
        else:
            path = filedialog.askopenfilename(
                filetypes=self.filetypes,
                initialdir=self.initialdir
            )
        if path:
            selected_path = Path(path)
            self.path_var.set(str(selected_path))
            if self.mode == "directory":
                self.display_name.set(str(selected_path))
            else:
                self.display_name.set(selected_path.name)
            if self.command:
                self.command(str(selected_path))

    def get(self) -> str:
        """Return the currently selected file path.

        Returns:
            str: Selected file or directory path.
        """
        return self.path_var.get()
    
    def set(self, value: Optional[str]):
        """Set the file path in the entry.

        Args:
            value: File or directory path to display.
        """
        if not value:
            self.path_var.set("")
            self.display_name.set("")
            return

        selected_path = Path(value)
        self.path_var.set(str(selected_path))
        if self.mode == "directory":
            self.display_name.set(str(selected_path))

        else:
            self.display_name.set(selected_path.name)

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the currently selected path.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for an invalid path selection.
        """
        selected_path = self.get().strip()
        if not selected_path:
            return self.apply_validation((False, "No path selected.", "error"))

        path = Path(selected_path)
        if self.mode == "directory":
            if not path.is_dir():
                return self.apply_validation((False, f"Directory does not exist: {selected_path}", "error"))
        else:
            if not path.is_file():
                return self.apply_validation((False, f"File does not exist: {selected_path}", "error"))

        return self.apply_validation((True, None, None))


if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

    root = BHoMBaseWindow()
    parent_container = root.content_frame

    def on_file_selected(path):
        """Print selected path in the standalone example."""
        print(f"Selected: {path}")

    path_selector = PathSelector(
        parent_container, 
        button_text="Select File", 
        filetypes=[("All Files", "*.*")], 
        command=on_file_selected,
        item_title="Path Selector",
        helper_text="Select a file from your system.",
        build_options=PackingOptions(padx=20, pady=20),
        button_width=15,
        entry_width=50,
        alignment="center"
    )
    path_selector.build()

    root.mainloop()