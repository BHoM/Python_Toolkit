import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

class ScrollableListBox(ttk.Frame):
    """A reusable listbox widget with auto-hiding scrollbar."""

    def __init__(self, parent, items=None, selectmode=tk.MULTIPLE, height=None, show_selection_controls=False,  item_title: Optional[str] = None, helper_text: Optional[str] = None, **kwargs):
        """
        Args:
            parent (tk.Widget): The parent widget.
            items (list, optional): List of items to populate the listbox.
            selectmode (str): Selection mode for the listbox (SINGLE, MULTIPLE, etc.).
            height (int, optional): Height of the listbox. Defaults to number of items.
            show_selection_controls (bool): Show Select All and Deselect All buttons.
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)
        
        self.items = items or []
        if height is None:
            height = len(self.items) if self.items else 5

        self.item_title = item_title
        self.helper_text = helper_text

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Header.TLabel")
            self.title_label.pack(side="top", anchor="w")

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
            self.helper_label.pack(side="top", anchor="w")
        
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self.content_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create listbox
        self.listbox = tk.Listbox(
            self.content_frame,
            selectmode=selectmode,
            height=height,
            yscrollcommand=self.scrollbar.set,
            exportselection=False,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)
        
        # Populate with items
        for item in self.items:
            self.listbox.insert(tk.END, item)
        
        # Auto-hide scrollbar when not needed
        self.listbox.bind("<Configure>", self._on_configure)
        self._on_configure()

        if show_selection_controls:
            controls = ttk.Frame(self)
            controls.pack(fill=tk.X, pady=(8, 0))

            self.select_all_button = ttk.Button(controls, text="Select All", command=self.select_all)
            self.select_all_button.pack(side=tk.LEFT)

            self.deselect_all_button = ttk.Button(controls, text="Deselect All", command=self.deselect_all)
            self.deselect_all_button.pack(side=tk.LEFT, padx=(8, 0))
    
    def _on_configure(self, event=None):
        """Hide scrollbar if all items fit in the visible area."""
        if self.listbox.size() <= int(self.listbox.cget("height")):
            self.scrollbar.pack_forget()
        else:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def set_selections(self, items):
        """Set the selection to the specified items."""
        self.listbox.selection_clear(0, tk.END)
        for index, item in enumerate(self.items):
            if item in items:
                self.listbox.selection_set(index)
    
    def get_selection(self):
        """Return a list of selected items."""
        selected_indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in selected_indices]
    
    def get_selection_indices(self):
        """Return tuple of selected indices."""
        return self.listbox.curselection()

    def select_all(self):
        """Select all items in the listbox."""
        self.listbox.selection_set(0, tk.END)

    def deselect_all(self):
        """Clear all selected items in the listbox."""
        self.listbox.selection_clear(0, tk.END)
    
    def insert(self, index, item):
        """Insert an item at the specified index."""
        self.listbox.insert(index, item)
        self._on_configure()
    
    def delete(self, index):
        """Delete an item at the specified index."""
        self.listbox.delete(index)
        self._on_configure()
    
    def clear(self):
        """Clear all items from the listbox."""
        self.listbox.delete(0, tk.END)
        self._on_configure()


if __name__ == "__main__":

    from python_toolkit.tkinter.DefaultRoot import DefaultRoot
    root = DefaultRoot()
    parent_container = root.content_frame
    
    items = [f"Item {i}" for i in range(1, 21)]
    listbox = ScrollableListBox(parent_container, items=items, height=10, show_selection_controls=True, item_title="List Box", helper_text="Select items from the list.")
    listbox.pack(padx=20, pady=20)

    print("Selected items:", listbox.get_selection())
    
    root.mainloop()