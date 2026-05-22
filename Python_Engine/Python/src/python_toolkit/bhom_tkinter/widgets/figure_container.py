"""Container widget for embedding matplotlib figures or image content."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from typing import Optional, Any, Literal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
import matplotlib as mpl


class FigureContainer(BHoMBaseWidget):
    """
    A reusable widget for embedding matplotlib figures and images.
    """

    def __init__(
        self,
        parent: ttk.Frame,
        auto_size: bool = False,
        rigid_width: Optional[int] = None,
        rigid_height: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Initialize the FigureContainer widget.

        Args:
            parent: Parent widget
            auto_size: If ``True``, fit content once to current frame size.
            rigid_width: Optional fixed target width (pixels) for content sizing.
            rigid_height: Optional fixed target height (pixels) for content sizing.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.auto_size = bool(auto_size)
        self.rigid_width = int(rigid_width) if rigid_width is not None else None
        self.rigid_height = int(rigid_height) if rigid_height is not None else None

        if self.rigid_width is not None:
            self.content_frame.config(width=self.rigid_width)

        if self.rigid_height is not None:
            self.content_frame.config(height=self.rigid_height)

        self.figure: Optional[Figure] = None
        self.image: Optional[Any] = None
        self.image_file: Optional[str] = None
        self._original_pil_image: Optional[Any] = None

        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.image_label: Optional[ttk.Label] = None
        self._fit_after_id: Optional[str] = None
        self._fit_attempts: int = 0

    def _clear_children(self) -> None:
        """Destroy any child widgets hosted by the content frame only."""
        if self._fit_after_id is not None:
            try:
                self.after_cancel(self._fit_after_id)
            except Exception:
                pass
            self._fit_after_id = None
        self._fit_attempts = 0
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.canvas = None
        self.image_label = None

    def _resolve_target_size(self) -> tuple[int, int]:
        """Resolve sizing target from rigid args or, optionally, frame dimensions."""
        if self.rigid_width is not None and self.rigid_height is not None:
            return self.rigid_width, self.rigid_height

        self.update_idletasks()

        if self.auto_size:
            frame_width = max(self.content_frame.winfo_width(), self.content_frame.winfo_reqwidth())
            frame_height = max(self.content_frame.winfo_height(), self.content_frame.winfo_reqheight())
            return frame_width, frame_height

        frame_width = self.rigid_width or 0
        frame_height = self.rigid_height or 0
        return frame_width, frame_height

    def _close_held_figure(self) -> None:
        """Close any currently held matplotlib figure to release resources."""
        if self.figure is not None:
            try:
                plt.close(self.figure)
            except Exception:
                pass
            self.figure = None

    def _resolved_background(self) -> str:
        """Resolve a background colour suitable for embedded Tk canvas widgets."""
        try:
            bg = ttk.Style().lookup("TFrame", "background")
            if bg:
                return bg
        except Exception:
            pass
        try:
            return self.winfo_toplevel().cget("bg")
        except Exception:
            return "white"

    def embed_figure(self, figure: Figure) -> None:
        """Embed a matplotlib figure in the container, replacing existing content.

        Args:
            figure: Matplotlib Figure object to embed.
        """
        self._close_held_figure()
        self._clear_children()
        self.figure = figure
        self.canvas = FigureCanvasTkAgg(figure, master=self.content_frame)
        bg_color = self._resolved_background()
        self.canvas.get_tk_widget().configure(bg=bg_color, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        if self.auto_size or self.rigid_width is not None or self.rigid_height is not None:
            self._fit_figure_once()
        else:
            self.canvas.draw_idle()

    def embed_image(self, image: tk.PhotoImage) -> None:
        """Embed a Tk image in the figure container.

        Args:
            image: Tk PhotoImage object to embed
        """
        self._close_held_figure()
        self._clear_children()
        self.image = image
        self._original_pil_image = None
        self.image_label = Label(self.content_frame, image=image)
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def embed_image_file(self, file_path: str) -> None:
        """Load and embed an image file, scaled to fit the container.

        Args:
            file_path: Path to image file
        """
        self.image_file = file_path
        try:
            from PIL import Image, ImageTk
            pil_image = Image.open(file_path)
            self._original_pil_image = pil_image
            self._close_held_figure()
            self._clear_children()
            self.image_label = Label(self.content_frame)
            self.image_label.pack(fill=tk.BOTH, expand=True)
            if self.auto_size or self.rigid_width is not None or self.rigid_height is not None:
                self._scale_image_to_fit_once()
            else:
                self.image = ImageTk.PhotoImage(self._original_pil_image)
                self.image_label.set(self.image)
        except ImportError:
            image = tk.PhotoImage(file=file_path)
            self._close_held_figure()
            self._clear_children()
            self.image = image
            self.image_label = Label(self.content_frame, image=image)
            self.image_label.pack(fill=tk.BOTH, expand=True)

    def _fit_figure_once(self) -> None:
        """Size the figure to the current frame once and stop resizing afterwards."""
        if self.figure is None or self.canvas is None:
            return

        frame_width, frame_height = self._resolve_target_size()

        if (self.rigid_width is not None) != (self.rigid_height is not None):
            dpi = float(self.figure.get_dpi())
            if dpi <= 0:
                dpi = 100.0
            current_w_in, current_h_in = self.figure.get_size_inches()
            aspect = (current_w_in / current_h_in) if current_h_in else 1.0
            if self.rigid_width is not None:
                frame_width = self.rigid_width
                frame_height = int(round(self.rigid_width / aspect)) if aspect else self.rigid_width
            else:
                frame_height = self.rigid_height or 0
                frame_width = int(round(frame_height * aspect))

        if frame_width <= 1 or frame_height <= 1:
            if not self.auto_size:
                self._fit_after_id = None
                return
            self._fit_attempts += 1
            if self._fit_attempts > 25:
                self._fit_after_id = None
                return
            self._fit_after_id = self.after(20, self._fit_figure_once)
            return

        try:
            dpi = float(self.figure.get_dpi())
            if dpi <= 0:
                dpi = 100.0
            self.figure.set_size_inches(frame_width / dpi, frame_height / dpi, forward=True)
            self.canvas.draw_idle()
        except Exception:
            self.canvas.draw_idle()
        finally:
            self._fit_after_id = None
            self._fit_attempts = 0

    def _scale_image_to_fit_once(self):
        """Scale the image to fit within the content frame while maintaining aspect ratio."""
        if self._original_pil_image is None:
            return

        frame_width, frame_height = self._resolve_target_size()

        if frame_width <= 1 or frame_height <= 1:
            if not self.auto_size:
                self._fit_after_id = None
                return
            self._fit_attempts += 1
            if self._fit_attempts > 25:
                self._fit_after_id = None
                return
            self._fit_after_id = self.after(20, self._scale_image_to_fit_once)
            return

        try:
            from PIL import Image, ImageTk
            img_width, img_height = self._original_pil_image.size
            scale = min(frame_width / img_width, frame_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized = self._original_pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.image = ImageTk.PhotoImage(resized)
            if self.image_label:
                self.image_label.set(self.image)
            self._fit_after_id = None
            self._fit_attempts = 0
        except Exception:
            pass

    def clear(self) -> None:
        """Clear the figure container."""
        self._close_held_figure()
        self._clear_children()
        self.image = None
        self.image_label = None
        self._original_pil_image = None
        self.image_file = None

    def get(self):
        """Return the currently embedded figure or image."""
        if self.figure is not None:
            return self.figure
        elif self.image is not None:
            return self.image
        return None

    def set(self, value):
        """Set the content of the figure container.

        Args:
            value: ``Figure``, ``PhotoImage``, or image file path string.
        """
        if isinstance(value, Figure):
            self.embed_figure(value)
        elif isinstance(value, tk.PhotoImage):
            self.embed_image(value)
        elif isinstance(value, str):
            self.embed_image_file(value)
        else:
            raise ValueError("Unsupported value type for FigureContainer. Must be Figure, PhotoImage, or file path string.")

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current content of the figure container."""
        if self.figure is not None:
            return self.apply_validation((True, None, None))
        if self.image is not None:
            return self.apply_validation((True, None, None))
        return self.apply_validation((False, "FigureContainer is empty. Please embed a figure or image.", "error"))


if __name__ == "__main__":
    import numpy as np
    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets.validated_entry_box import ValidatedEntryBox
    from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions

    def make_plot(freq: float) -> Figure:
        x = np.linspace(0, 2 * np.pi, 300)
        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.plot(x, np.sin(freq * x))
        ax.set_title(f"sin({freq:.1f}x)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        fig.tight_layout()
        return fig

    root = BHoMBaseWindow(title="FigureContainer Demo", grid_dimensions=(2, 1))

    figure_widget = FigureContainer(
        root.content_frame,
        item_title="Plot Preview",
        rigid_width=400,
        rigid_height=250,
        build_options=GridOptions(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10)),
    )
    figure_widget.build()
    figure_widget.embed_figure(make_plot(2.0))

    def on_freq_change(value):
        try:
            freq = float(value)
        except (ValueError, TypeError):
            return
        figure_widget.embed_figure(make_plot(freq))

    freq_input = ValidatedEntryBox(
        root.content_frame,
        item_title="Frequency",
        helper_text="Change the frequency to update the plot.",
        on_change=on_freq_change,
        build_options=GridOptions(row=0, column=0, sticky="ew", padx=10, pady=(10, 4)),
    )
    freq_input.set("2")
    freq_input.build()

    root.content_frame.columnconfigure(0, weight=1)
    root.content_frame.rowconfigure(1, weight=1)

    root.mainloop()
