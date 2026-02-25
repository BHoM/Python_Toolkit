"""Standardized warning dialog window for errors, warnings, and info messages."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from typing import Optional
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow


class WarningBox(BHoMBaseWindow):
    """Show categorized messages using the shared BHoM window styling."""

    def __init__(
            self, 
            title: str= 'Warning', 
            warnings: list[str] | str | None = None,
            errors: list[str] | str | None = None,
            infos: list[str] | str | None = None,
            **kwargs
            ):

        self.warnings = self._normalise_messages(warnings)
        self.errors = self._normalise_messages(errors)
        self.infos = self._normalise_messages(infos)

        super().__init__(
            title=title,
            show_submit=False,
            close_text="Continue",
            min_width=250,
            min_height=150,  
            **kwargs
        )

    def build(self):
        """Render current messages into the content area."""
        self._render_messages()
        super().build()

    def _normalise_messages(self, messages: list[str] | str | None) -> list[str]:
        if messages is None:
            return []
        if isinstance(messages, str):
            return [messages]
        return list(messages)

    def _render_messages(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        for message in self.errors:
            Label(self.content_frame, text=message, style="Error.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.warnings:
            Label(self.content_frame, text=message, style="Warning.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))
        for message in self.infos:
            Label(self.content_frame, text=message, style="Caption.TLabel", wraplength=400, justify=tk.LEFT).pack(anchor="w", pady=(0, 5))

    def update_messages(self):
        """Clear and re-render all messages in the warning box."""
        self._render_messages()
        self.refresh_sizing()


    def add_error_message(self, message: str):
        """Add an error message to the warning box.

        Args:
            message: Error text to append.
        """
        self.errors.append(message)
        self.update_messages()

    def add_warning_message(self, message: str):
        """Add a warning message to the warning box.

        Args:
            message: Warning text to append.
        """
        self.warnings.append(message)
        self.update_messages()

    def add_info_message(self, message: str):
        """Add an informational message to the warning box.

        Args:
            message: Informational text to append.
        """
        self.infos.append(message)
        self.update_messages()


if __name__ == "__main__":
    root = WarningBox(title="Validation Error", warnings="This is a warning message to alert the user about something important.")

    for message in ["This is the first error message.", "This is the second error message."]:
        root.add_error_message(message)

    root.add_info_message("This is some additional information for the user.")
    root.mainloop()