import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

class PathSelector(ttk.Frame):
    """A reusable path/file selector widget with a button and a readonly entry."""

    def __init__(self, parent, button_text="Browse...", filetypes=None, command=None, initialdir=None, mode="file", **kwargs):
        """
        Args:
            parent (tk.Widget): The parent widget.
            button_text (str): The text to display on the button.
            filetypes (list, optional): List of filetypes for the dialog.
            command (callable, optional): Called with the file path after selection.
            initialdir (str, optional): Initial directory for the file dialog.
            mode (str): Either "file" or "directory" to select files or directories.
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)
        self.path_var = tk.StringVar()
        self.command = command
        self.filetypes = filetypes
        self.initialdir = initialdir
        self.mode = mode

        self.display_name = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.display_name, width=40)
        self.entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)

        self.button = ttk.Button(self, text=button_text, command=self._on_click)
        self.button.pack(side=tk.LEFT)

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

    def get(self):
        """Return the currently selected file path."""
        return self.path_var.get()
    
    def set(self, path):
        """Set the file path in the entry."""
        selected_path = Path(path)
        self.path_var.set(str(selected_path))
        if self.mode == "directory":
            self.display_name.set(str(selected_path))

        else:
            self.display_name.set(selected_path.name)


if __name__ == "__main__":
    # Test the file selector widget
    root = tk.Tk()
    root.title("File Selector Test")

    def on_file_selected(path):
        print(f"Selected: {path}")

    path_selector = PathSelector(root, button_text="Select File", filetypes=[("All Files", "*.*")], command=on_file_selected)
    path_selector.pack(padx=20, pady=20)

    root.mainloop()