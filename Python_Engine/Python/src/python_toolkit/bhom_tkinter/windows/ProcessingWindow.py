import tkinter as tk
from tkinter import ttk
import os
import time
from typing import Optional
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

class ProcessingWindow(BHoMBaseWindow):
    """A simple processing window with animated indicator."""

    def __init__(self, title="Processing", message="Processing..."):
        """
        Args:
            title (str): Window title.
            message (str): Message to display.
        """
        super().__init__(title=title, min_width=300, min_height=150, show_submit=False, show_close=False)
        
        self.title(title)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Container
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        # Constant title label
        self.title_label = ttk.Label(
            container,
            text=title,
            style="Title.TLabel",
            justify="center",
            wraplength=400
        )
        self.title_label.pack(pady=(0, 8))

        # Updatable message label
        self.message_label = ttk.Label(
            container,
            text=message,
            justify="center",
            wraplength=400
        )
        self.message_label.pack(pady=(0, 20))

        # Animation frame
        animation_frame = ttk.Frame(container)
        animation_frame.pack(expand=True)

        self.animation_label = ttk.Label(
            animation_frame,
            text="●",
            style="Title.TLabel",
            foreground="#0078d4"
        )
        self.animation_label.pack()

        # Animation state
        self.animation_frames = ["●", "●", "●"]
        self.current_frame = 0
        self.is_running = False

        # Update to calculate the required size
        self.update_idletasks()
        
        # Get the required width and height
        required_width = self.winfo_reqwidth()
        required_height = self.winfo_reqheight()
        
        # Set minimum size
        min_width = 300
        min_height = 150
        window_width = max(required_width, min_width)
        window_height = max(required_height, min_height)

        # Center on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def start(self):
        """Start the processing window and animation."""
        self.is_running = True
        self._animate()

    def keep_alive(self):
        """Call this repeatedly to process animation updates. Returns False when done."""
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
            self.animation_label.config(text=dots[self.current_frame % len(dots)])
            self.current_frame += 1
            self.after(200, self._animate)

    def update_message(self, message: str):
        """Update the message text."""
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
