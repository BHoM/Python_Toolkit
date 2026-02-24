import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow


class LandingPage(BHoMBaseWindow):
    """
    A reusable landing page GUI with configurable title, message, and buttons.
    Uses BHoMBaseWindow as the base template.
    """

    def __init__(
        self,
        title: str = "Landing Page",
        header: Optional[str] = None,
        message: Optional[str] = None,
        sub_title: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes the landing page GUI.

        Args:
            title (str): Window and header title text.
            message (str, optional): Commentary/message text to display.
        """
        self.header = header
        self.message = message
        self.sub_title = sub_title
        self.custom_buttons_frame: Optional[ttk.Frame] = None

        super().__init__(
            title=title,
            **kwargs,
        )

    def build(self):
        """Build landing-page content using the base window's content area."""
        if self.header:
            ttk.Label(self.content_frame, text=self.header, style="Header.TLabel").pack(
                side="top", anchor="w", pady=(0, 10)
            )

        if self.message:
            ttk.Label(
                self.content_frame,
                text=self.message,
                style="Body.TLabel",
                justify=tk.LEFT,
            ).pack(side="top", anchor="w", pady=(0, 10))
        
        if self.sub_title:
            ttk.Label(self.content_frame, text=self.sub_title, style="Caption.TLabel").pack(
                side="top", anchor="w", pady=(0, 10)
            )

        self.custom_buttons_frame = ttk.Frame(self.content_frame)
        self.custom_buttons_frame.pack(fill=tk.X, pady=(0, 20))

        super().build()

    def add_custom_button(self, text: str, command: Callable, **kwargs) -> ttk.Button:
        """
        Add a custom button to the landing page.

        Args:
            text (str): Button text.
            command (callable): Function to call when button is clicked.
            **kwargs: Additional ttk.Button options.

        Returns:
            ttk.Button: The created button widget.
        """
        if self.custom_buttons_frame is None:
            self.custom_buttons_frame = ttk.Frame(self.content_frame)
            self.custom_buttons_frame.pack(fill=tk.X, pady=(0, 20))

        button = ttk.Button(self.custom_buttons_frame, text=text, command=command, **kwargs)
        button.pack(pady=5, fill=tk.X)
        # Recalculate window size after adding button
        self.refresh_sizing()
        return button


if __name__ == "__main__":

    #simple example of using the landing page
    def on_button_click():
        print("Button clicked!")

    landing_page = LandingPage(
        title="Welcome to the BHoM Toolkit",
        header="Welcome to the BHoM Toolkit",
        message="This is a landing page example. You can add custom buttons below.",
        sub_title="Please click the button to proceed.",
    )
    landing_page.add_custom_button(text="Click Me", command=on_button_click)
    landing_page.mainloop()