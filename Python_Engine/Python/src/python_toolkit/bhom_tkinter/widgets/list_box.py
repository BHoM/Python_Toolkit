"""Scrollable listbox widget with optional selection helper controls."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button

class ScrollableListBox(BHoMBaseWidget):
    """A reusable listbox widget with auto-hiding scrollbar."""

    def __init__(
            self, 
            parent: ttk.Frame, 
            items=None, 
            selectmode=tk.MULTIPLE, 
            height=None,
            width=None,
            show_selection_controls=False,
            **kwargs):
        """
        Args:
            parent (ttk.Frame): The parent widget.
            items (list, optional): List of items to populate the listbox.
            selectmode (str): Selection mode for the listbox (SINGLE, MULTIPLE, etc.).
            height (int, optional): Height of the listbox. Defaults to number of items.
            width (int, optional): Width of the listbox in characters. If None, listbox expands to fill available space.
            show_selection_controls (bool): Show Select All and Deselect All buttons.
            **kwargs: Additional Frame options.
        """
        super().__init__(parent, **kwargs)
        
        self.items = items or []
        if height is None:
            height = len(self.items) if self.items else 5

        # Create scrollbar
        self.scrollbar = ttk.Scrollbar(self.content_frame)

        self.content_frame.columnconfigure(0, weight=1) 
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=1)
        
        # Create listbox
        listbox_options = {
            "selectmode": selectmode,
            "height": height,
            "yscrollcommand": self.scrollbar.set,
            "exportselection": False,
        }
        if width is not None:
            listbox_options["width"] = width
        
        self.listbox = tk.Listbox(self.content_frame, **listbox_options)
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.scrollbar.config(command=self.listbox.yview)
        
        # Populate with items
        for item in self.items:
            self.listbox.insert(tk.END, item)
        
        # Auto-hide scrollbar when not needed
        self.listbox.bind("<Configure>", self._on_configure)
        self._on_configure()

        if show_selection_controls:

            select_widget = Button(self.content_frame, text="Select All", command=self.select_all)
            select_widget.grid(row=1, column=0, sticky="ns", padx=(0, 4), pady=(8, 0))
            self.select_all_button = select_widget.button

            deselect_widget = Button(self.content_frame, text="Deselect All", command=self.deselect_all)
            deselect_widget.grid(row=1, column=1, sticky="ns", padx=(4, 0), pady=(8, 0))
            self.deselect_all_button = deselect_widget.button
    
    def _on_configure(self, event=None):
        """Hide scrollbar if all items fit in the visible area."""
        if self.listbox.size() <= int(self.listbox.cget("height")):
            self.scrollbar.grid_forget()
        else:
            self.scrollbar.grid(row=0, column=1, sticky="ns")

    def set_selections(self, items):
        """Set the selection to the specified items.

        Args:
            items: Item values to select.
        """
        self.listbox.selection_clear(0, tk.END)
        for index, item in enumerate(self.items):
            if item in items:
                self.listbox.selection_set(index)
    
    def get_selection(self):
        """Return a list of selected items.

        Returns:
            list: Selected item values.
        """
        selected_indices = self.listbox.curselection()
        return [self.listbox.get(i) for i in selected_indices]
    
    def get_selection_indices(self):
        """Return tuple of selected indices.

        Returns:
            tuple: Indices of selected entries.
        """
        return self.listbox.curselection()

    def select_all(self):
        """Select all items in the listbox."""
        self.listbox.selection_set(0, tk.END)

    def deselect_all(self):
        """Clear all selected items in the listbox."""
        self.listbox.selection_clear(0, tk.END)
    
    def insert(self, index, item):
        """Insert an item at the specified index.

        Args:
            index: Position at which to insert.
            item: Item value to insert.
        """
        self.listbox.insert(index, item)
        self._on_configure()
    
    def delete(self, index):
        """Delete an item at the specified index.

        Args:
            index: Position of item to delete.
        """
        self.listbox.delete(index)
        self._on_configure()
    
    def clear(self):
        """Clear all items from the listbox."""
        self.listbox.delete(0, tk.END)
        self._on_configure()

    def pack(self, **kwargs):
        """Pack the widget with the given options.

        Args:
            **kwargs: Pack geometry manager options.
        """
        super().pack(**kwargs)
        self._on_configure()  # Ensure scrollbar visibility is updated when packed

    def set(self, value):
        """Set the listbox items to the provided list.

        Args:
            value: Iterable of item values to display.
        """
        self.clear()
        for item in value:
            self.listbox.insert(tk.END, item)
        self._on_configure()
    
    def get(self):
        """Get the current list of items in the listbox.

        Returns:
            list: Current listbox items in display order.
        """
        return [self.listbox.get(i) for i in range(self.listbox.size())]
    
    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current listbox state.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for an invalid state.
        """
        # In this simple implementation, all states are valid, so we return True.
        return self.apply_validation((True, None, None))


if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

    root = BHoMBaseWindow()
    parent_container = root.content_frame
    
    items = [f"Item {i}" for i in range(1, 21)]
    root.widgets.append(ScrollableListBox(
        parent_container, 
        items=items, 
        height=10, 
        show_selection_controls=True, 
        item_title="List Box", 
        helper_text="Select items from the list.",
        build_options=PackingOptions(padx=10, pady=10)
    ))
    root.widgets[-1].build()

    print("Selected items:", root.widgets[-1].get())
    
    root.mainloop()