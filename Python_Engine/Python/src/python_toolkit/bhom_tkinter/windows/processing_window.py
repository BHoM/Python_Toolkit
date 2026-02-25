"""Window that displays a status message with a lightweight animated indicator."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
import time
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

class ProcessingWindow(BHoMBaseWindow):
    """A simple processing window with animated indicator."""

    def __init__(self, title="Processing", message="Processing..."):
        """
        Args:
            title (str): Window title.
            message (str): Message to display.
        """
        self.window_title = title
        self.message_text = message

        super().__init__(
            title=title,
            min_width=300,
            min_height=150,
            show_submit=False,
            show_close=False,
            resizable=False,
        )

        self.attributes("-topmost", True)

        self.title_label = None
        self.message_label = None
        self.animation_label = None

        # Animation state
        self.current_frame = 0
        self.is_running = False

    def build(self):
        """Build processing labels and the animation indicator."""
        self.title_label = Label(
            self.content_frame,
            text=self.window_title,
            style="Title.TLabel",
            justify="center",
            wraplength=400,
        )
        self.title_label.pack(pady=(0, 8))

        self.message_label = Label(
            self.content_frame,
            text=self.message_text,
            justify="center",
            wraplength=400,
        )
        self.message_label.pack(pady=(0, 20))

        self.animation_label = Label(
            self.content_frame,
            text="●",
            style="Title.TLabel",
        )
        self.animation_label.pack()

        super().build()

    def start(self):
        """Start the processing window and animation."""
        self.is_running = True
        self._animate()

    def keep_alive(self):
        """Call repeatedly to process animation updates.

        Returns:
            bool: `True` while running and window exists, else `False`.
        """
        if self.is_running and self.winfo_exists():
            self.update()
            return True
        return False

    def stop(self):
        """Stop the animation and close the window."""
        self.is_running = False
        self.destroy()

    def _animate(self):
        """Update animation frames."""
        if self.is_running:
            # Create rotating dot animation
            dots = ["◐", "◓", "◑", "◒"]
            if self.animation_label is not None:
                self.animation_label.config(text=dots[self.current_frame % len(dots)])
            self.current_frame += 1
            self.after(200, self._animate)

    def update_message(self, message: str):
        """Update the message text.

        Args:
            message: New status message to display.
        """
        self.message_text = message
        if self.message_label is not None:
            self.message_label.config(text=message)
        self.update()


if __name__ == "__main__":
    # Test the processing window
    
    processing = ProcessingWindow(title="Test Processing", message="Running Test Calculation...")
    processing.start()
    
    # Simulate some work
    for i in range(50):
        time.sleep(0.1)
        processing.update_message(f"Running Test Calculation... {i+1}/50")
    processing.stop()
