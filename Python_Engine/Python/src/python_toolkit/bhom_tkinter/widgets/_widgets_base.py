from abc import ABC, abstractmethod

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal, Union

from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

from uuid import uuid4

class BHoMBaseWidget(ttk.Frame, ABC):
    """
    Base class for all widgets in the BHoM Tkinter toolkit.
    Provides common structure and functionality for consistent design.
    """

    def __init__(
            self, 
            parent: ttk.Frame, 
            id: Optional[str] = None, 
            item_title: Optional[str] = None, 
            helper_text: Optional[str] = None, 
            packing_options: PackingOptions = PackingOptions(),
            **kwargs):
        """
        Initialize the widget base.

        Args:
            parent: Parent widget
            id: Optional unique identifier for the widget
            item_title: Optional header text shown at the top of the widget frame.
            helper_text: Optional helper text shown above the entry box.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.item_title = item_title
        self.helper_text = helper_text
        self.packing_options = packing_options

        if id is None:
            self.id = str(uuid4())
        else:
            self.id = id

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Header.TLabel")
            self.title_label.pack(side="top", anchor="w")

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
            self.helper_label.pack(side="top", anchor="w")

        # Container frame for embedded content (not title/helper)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="top", fill=tk.BOTH, expand=True)

    @abstractmethod
    def get(self):
        """Get the current value of the widget."""
        raise NotImplementedError("Subclasses must implement the get() method.")

    @abstractmethod
    def set(self, value):
        """Set the value of the widget."""
        raise NotImplementedError("Subclasses must implement the set() method.")
    
    def build(
            self, 
            build_type: Literal['pack', 'grid', 'place'] = 'pack',
            **kwargs
        ):
        """Pack the widget into the parent container."""
        if build_type == 'pack':
            self.pack(**self.packing_options.to_dict())

        elif build_type == 'grid':
            raise NotImplementedError("Grid packing is not yet implemented for BHoMBaseWidget.")
        
        elif build_type == 'place':
            raise NotImplementedError("Place packing is not yet implemented for BHoMBaseWidget.")
