import tkinter as tk
from tkinter import ttk
import os

import time
import threading

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

class ProcessingWindow(BHoMBaseWindow):
    """A simple processing window with animated indicator."""

    def __init__(self, title="Processing", message="Processing...", *args, **kwargs):
        """
        Args:
            title (str): Window title.
            message (str): Message to display.
        """
        super().__init__(
            title=title,
            min_width=300,
            min_height=150,
            width=400,
            height=200,
            theme_mode="auto",
            show_close=False,
            show_submit=False,
            *args,
            **kwargs
        )
        
        self.title(title)
        self.attributes("-topmost", True)
        self.resizable(False, False)

        # Container
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        # Message label (to calculate size)
        self.message_label = ttk.Label(
            container,
            text=message,
            style="Title.TLabel",
            justify="center",
            wraplength=400
        )
        try:
            title_font = ttk.Style(self).lookup("Title.TLabel", "font")
            if title_font:
                self.message_label.configure(font=title_font)
        except Exception:
            pass
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
        try:
            title_font = ttk.Style(self).lookup("Title.TLabel", "font")
            if title_font:
                self.animation_label.configure(font=title_font)
        except Exception:
            pass
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
        if self.is_running:
            return
        self.is_running = True

        # Run the Tk mainloop on the calling thread (must be main thread on many platforms).
        try:
            self._animate()
            self.mainloop()
        except Exception as e:
            print("ProcessingWindow mainloop error:", e)
            raise

    def start_with_worker(self, worker, args=(), kwargs=None):
        """Start the GUI mainloop on this (main) thread and run `worker` in a background thread.

        The worker should not call Tkinter methods directly. When the worker finishes,
        the window is closed via a call scheduled on the Tk event loop.
        """
        if kwargs is None:
            kwargs = {}

        if self.is_running:
            return
        self.is_running = True

        def run_worker():
            try:
                worker(*args, **kwargs)
            finally:
                try:
                    self.after(0, self.stop)
                except Exception:
                    pass

        t = threading.Thread(target=run_worker, daemon=True)
        t.start()

        try:
            self._animate()
            self.mainloop()
        except Exception as e:
            print("ProcessingWindow mainloop error:", e)
            raise

    def keep_alive(self):
        """Call this repeatedly to process animation updates. Returns False when done."""
        if self.is_running and self.winfo_exists():
            self.update()
            return True
        return False

    def stop(self):
        """Stop the animation and close the window."""
        self.is_running = False
        try:
            # Stop the mainloop if running and then destroy the window
            if self.winfo_exists():
                try:
                    self.quit()
                except Exception:
                    pass
                try:
                    self.destroy()
                except Exception:
                    pass
        except Exception:
            pass

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
        try:
            self.message_label.config(text=message)
            # schedule an idle update so the UI refreshes promptly
            self.update_idletasks()
        except Exception:
            pass


if __name__ == "__main__":
    # Test the processing window
    
    processing = ProcessingWindow(title="Test Processing", message="Running Comfort and Safety Calculation...")
    def worker():
        for i in range(50):
            time.sleep(0.1)
            try:
                processing.after(0, processing.update_message, f"Step {i+1}/50")
            except Exception:
                pass

    processing.start_with_worker(worker)
