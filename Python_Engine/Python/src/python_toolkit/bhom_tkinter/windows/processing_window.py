"""Window that displays a status message with a lightweight animated indicator."""

import tkinter as tk
from tkinter import ttk
import time

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets.label import Label


class ProcessingWindow(BHoMBaseWindow):
    """A processing window with animated indicator, built on the BHoM window protocol."""

    def __init__(self, title="Processing", message="Processing..."):
        self.window_title = title
        self.message_text = message
        self.message_label = None
        self.animation_label = None
        self.current_frame = 0
        self.is_running = False
        self._after_id = None

        super().__init__(
            title=title,
            min_width=300,
            min_height=150,
            show_submit=False,
            show_close=False,
            resizable=False,
        )

        self.root = self
        self.attributes("-topmost", True)

    def build(self):
        """Build processing labels and the animation indicator."""
        container = ttk.Frame(self.content_frame)
        container.pack(fill=tk.BOTH, expand=True)

        self.message_label = Label(
            container,
            text=self.message_text,
            style="Title.TLabel",
            justify="center",
            wraplength=400,
            alignment="center",
        )
        self.message_label.pack(fill=tk.X, pady=(0, 20))

        animation_frame = ttk.Frame(container)
        animation_frame.pack(expand=True)

        self.animation_label = ttk.Label(
            animation_frame,
            text="●",
            style="Title.TLabel",
            justify="center",
            anchor="center",
        )
        self.animation_label.pack()

        super().build()

    def start(self):
        """Start the processing window and animation."""
        if self.is_running:
            return
        self.is_running = True
        self.current_frame = 0
        self._animate()

    def keep_alive(self):
        """Call this repeatedly to process animation updates. Returns False when done."""
        try:
            if self.is_running and self.root.winfo_exists():
                self.root.update_idletasks()
                self.root.update()
                return True
        except tk.TclError:
            return False
        return False

    def stop(self):
        """Stop the animation and close the window."""
        self.is_running = False
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self.destroy_root()

    def _animate(self):
        """Update animation frames."""
        if self.is_running and self.root.winfo_exists():
            dots = ["◐", "◓", "◑", "◒"]
            self.animation_label.config(text=dots[self.current_frame % len(dots)])
            self.current_frame += 1
            self._after_id = self.root.after(200, self._animate)

    def update_message(self, message: str):
        """Update the message text."""
        self.message_text = message
        if self.root.winfo_exists() and self.message_label is not None:
            self.message_label.set(message)
            self.root.update_idletasks()
            self.root.update()


if __name__ == "__main__":
    processing = ProcessingWindow(title="Test Processing", message="Running Comfort and Safety Calculation...")
    processing.start()

    for _ in range(50):
        time.sleep(0.1)
        processing.keep_alive()

    processing.stop()
