import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from DefaultRoot import DefaultRoot


class LandingPage(DefaultRoot):
    """
    A reusable landing page GUI with configurable title, message, and buttons.
    Uses DefaultRoot as the base template.
    """

    def __init__(
        self,
        title: str = "Landing Page",
        header: Optional[str] = None,   
        message: Optional[str] = None,
        sub_title: Optional[str] = None,
        min_width: int = 400,
        min_height: int = 200,
        show_continue: bool = True,
        continue_text: str = "Continue",
        continue_command: Optional[Callable] = None,
        show_close: bool = True,
        close_text: str = "Close",
        close_command: Optional[Callable] = None,
    ):
        """
        Initializes the landing page GUI.

        Args:
            title (str): Window and header title text.
            message (str, optional): Commentary/message text to display.
            min_width (int): Minimum window width in pixels.
            min_height (int): Minimum window height in pixels.
            show_continue (bool): Whether to show the continue button.
            continue_text (str): Text for the continue button.
            continue_command (callable, optional): Command to run on continue.
            show_close (bool): Whether to show the close button.
            close_text (str): Text for the close button.
            close_command (callable, optional): Command to run on close.
        """
        # Store callbacks
        self.continue_command = continue_command
        self.close_command = close_command
        super().__init__(
            title=title,
            min_width=min_width,
            min_height=min_height,
            show_submit=show_continue,
            submit_text=continue_text,
            submit_command=self._on_continue,
            show_close=show_close,
            close_text=close_text,
            close_command=self._on_close,
            )
        # Initialize DefaultRoot with continue mapped to submit

        if header:
            header_label = ttk.Label(self.content_frame, text=header, style="Header.TLabel")
            header_label.pack(side="top", anchor="w", pady=(0, 10))

        # Optional message/commentary
        if message:
            message_label = ttk.Label(self.content_frame, text=message, style="Body.TLabel", justify=tk.LEFT)
            message_label.pack(side="top", anchor="w", pady=(0, 10))
        
        # Optional sub-title
        if sub_title:
            sub_title_label = ttk.Label(self.content_frame, text=sub_title, style="Caption.TLabel")
            sub_title_label.pack(side="top", anchor="w", pady=(0, 10))

        # Custom buttons container
        self.custom_buttons_frame = ttk.Frame(self.content_frame)
        self.custom_buttons_frame.pack(fill=tk.X, pady=(0, 20))

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
        button = ttk.Button(self.custom_buttons_frame, text=text, command=command, **kwargs)
        button.pack(pady=5, fill=tk.X)
        # Recalculate window size after adding button
        self.refresh_sizing()
        return button

    def _on_continue(self):
        """Handle continue button click."""
        if self.continue_command:
            self.continue_command()

    def _on_close(self):
        """Handle close button click."""
        if self.close_command:
            self.close_command()

    def run(self) -> Optional[str]:
        """Show the landing page and return the result."""
        result = self.run()
        # Map DefaultRoot results to LandingPage convention
        if result == "submit":
            return "continue"
        return result


if __name__ == "__main__":
    # Basic example
    def on_continue():
        print("Continue clicked!")

    def on_close():
        print("Close clicked!")

    landing = LandingPage(
        title="Example Application",
        message="Welcome to the landing page example.\n\nThis demonstrates a configurable landing page with custom buttons.\n\nPlease select an option below to proceed.",
        header="Welcome!",
        sub_title="Please choose an option to continue:",
        continue_text="Proceed",
        continue_command=on_continue,
        close_command=on_close,
    )

    # Add custom buttons
    landing.add_custom_button("Option A", lambda: print("Option A selected"))
    landing.add_custom_button(
        "Option B", lambda: print("Option B selected")
    )

    landing.mainloop()

    result = landing.result


    print(f"Result: {result}")
