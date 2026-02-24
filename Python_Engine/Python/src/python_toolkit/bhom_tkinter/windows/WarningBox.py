import tkinter as tk
from tkinter import ttk
import os
import time
from typing import Optional, Literal
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

"""This will be used in place of warning / pop up boxes, to ensure consistent style"""


class WarningBox(BHoMBaseWindow):

    def __init__(
            self, 
            title: str= 'Warning', 
            warnings: list[str]|str = [], 
            errors: list[str]|str = [], 
            infos: list[str]|str = [], 
            **kwargs
            ):
        super().__init__(
            title=title,
            show_submit=False,
            close_text="Continue",
            min_width=250,
            min_height=150,  
            **kwargs
        )

        if isinstance(warnings, str):
            warnings = [warnings]
        if isinstance(errors, str):
            errors = [errors]
        if isinstance(infos, str):
            infos = [infos]

        self.warnings = warnings
        self.errors = errors
        self.infos = infos

        for message in self.errors:
            ttk.Label(self.content_frame, text=message, style="Error.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.warnings:
            ttk.Label(self.content_frame, text=message, style="Warning.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.infos:
            ttk.Label(self.content_frame, text=message, style="Caption.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))

    def update_messages(self):
        """Clear and re-render all messages in the warning box."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        for message in self.errors:
            ttk.Label(self.content_frame, text=message, style="Error.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.warnings:
            ttk.Label(self.content_frame, text=message, style="Warning.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.infos:
            ttk.Label(self.content_frame, text=message, style="Caption.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))


    def add_error_message(self, message: str):
        """Add an error message to the warning box."""
        self.errors.append(message)
        self.update_messages()

    def add_warning_message(self, message: str):
        """Add a warning message to the warning box."""
        self.warnings.append(message)
        self.update_messages()

    def add_info_message(self, message: str):
        """Add an informational message to the warning box."""
        self.infos.append(message)
        self.update_messages()


if __name__ == "__main__":
    root = WarningBox(title="Validation Error", warnings="This is a warning message to alert the user about something important.")

    for message in ["This is the first error message.", "This is the second error message."]:
        root.add_error_message(message)

    root.add_info_message("This is some additional information for the user.")
    root.mainloop()