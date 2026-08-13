import tkinter as tk
from tkinter import ttk
import os

import time
import threading

from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow

class ProcessingWindow(BHoMBaseChildWindow):
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
            show_banner=False,
            top_most=True,
            *args,
            **kwargs
        )

        self.attributes("-topmost", True)
        self.resizable(False, False)

        container = ttk.Frame(self.content_frame, padding=20)
        container.pack(fill="both", expand=True)

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

        self.animation_frames = ["●", "●", "●"]
        self.current_frame = 0
        self.is_running = False

        self.update_idletasks()
        self.refresh_sizing()


    def start(self):
        """Start the processing window and animation."""
        if self.is_running:
            return
        self.is_running = True

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
        self.destroy_root()

    def _animate(self):
        """Update animation frames."""
        if self.is_running:
            dots = ["◐", "◓", "◑", "◒"]
            self.animation_label.config(text=dots[self.current_frame % len(dots)])
            self.current_frame += 1
            self.after(200, self._animate)

    def update_message(self, message: str):
        """Update the message text."""
        try:
            self.message_label.config(text=message)
            self.update_idletasks()
        except Exception:
            pass


if __name__ == "__main__":
    processing = ProcessingWindow(title="Test Processing", message="Running Comfort and Safety Calculation...")
    def worker():
        for i in range(50):
            time.sleep(0.1)
            try:
                processing.after(0, processing.update_message, f"Step {i+1}/50")
            except Exception:
                pass

    processing.start_with_worker(worker)
