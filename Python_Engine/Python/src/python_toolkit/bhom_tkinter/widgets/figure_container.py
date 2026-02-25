"""Container widget for embedding matplotlib figures or image content."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from typing import Optional, Any
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
        **kwargs
    ) -> None:
        """
        Initialize the FigureContainer widget.

        Args:
            parent: Parent widget
            item_title: Optional header text shown at the top of the widget frame.
            helper_text: Optional helper text shown above the entry box.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.figure: Optional[Figure] = None
        self.image: Optional[Any] = None
        self.image_file: Optional[str] = None
        self._original_pil_image: Optional[Any] = None

        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.image_label: Optional[ttk.Label] = None

        if self.image:
            self.embed_image(self.image)

        elif self.figure:
            self.embed_figure(self.figure)

        elif self.image_file:
            self.embed_image_file(self.image_file)

    def _clear_children(self) -> None:
        """Destroy any child widgets hosted by the content frame only."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.canvas = None
        self.image_label = None

    def _resolved_background(self) -> str:
        """Resolve a background colour suitable for embedded Tk canvas widgets.

        Returns:
            str: Resolved background colour string.
        """
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

        self._clear_children()

        self.figure = figure
        self.canvas = FigureCanvasTkAgg(figure, master=self.content_frame)
        
        # Set canvas background to match the frame background for transparency
        bg_color = self._resolved_background()
        self.canvas.get_tk_widget().configure(bg=bg_color, highlightthickness=0)
        
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def embed_image(self, image: tk.PhotoImage) -> None:
        """
        Embed a Tk image in the figure container.
        Note: For automatic scaling, use embed_image_file() instead with PIL support.

        Args:
            image: Tk PhotoImage object to embed
        """
        self._clear_children()

        self.image = image
        self._original_pil_image = None
        
        # Create label to display the image
        self.image_label = Label(self.content_frame, image=image)
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def embed_image_file(self, file_path: str) -> None:
        """
        Load and embed an image file, scaled to fit the container.

        Args:
            file_path: Path to image file
        """
        self.image_file = file_path
        self._clear_children()
        
        try:
            from PIL import Image, ImageTk
            
            # Load with PIL for better scaling
            pil_image = Image.open(file_path)
            self._original_pil_image = pil_image
            
            # Create label
            self.image_label = Label(self.content_frame)
            self.image_label.pack(fill=tk.BOTH, expand=True)
            
            # Scale and display
            self.content_frame.bind("<Configure>", lambda e: self._scale_image_to_fit())
            self._scale_image_to_fit()
            
        except ImportError:
            # Fallback to basic PhotoImage without scaling
            image = tk.PhotoImage(file=file_path)
            self.image = image
            self.image_label = Label(self.content_frame, image=image)
            self.image_label.pack(fill=tk.BOTH, expand=True)
    
    def _scale_image_to_fit(self):
        """Scale the image to fit within the content frame while maintaining aspect ratio."""
        if self._original_pil_image is None:
            return
        
        # Get current frame dimensions
        frame_width = self.content_frame.winfo_width()
        frame_height = self.content_frame.winfo_height()
        
        # Skip if frame not yet sized
        if frame_width <= 1 or frame_height <= 1:
            return
        
        try:
            from PIL import Image, ImageTk
            
            # Calculate scaling factor to fit
            img_width, img_height = self._original_pil_image.size
            scale_width = frame_width / img_width
            scale_height = frame_height / img_height
            scale = min(scale_width, scale_height)
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            resized = self._original_pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and update label
            self.image = ImageTk.PhotoImage(resized)
            if self.image_label:
                self.image_label.configure(image=self.image)
        except Exception:
            pass  # Silently handle scaling errors

    def clear(self) -> None:
        """Clear the figure container."""
        self._clear_children()
        # Close any held figure to free matplotlib resources
        if self.figure is not None:
            try:
                plt.close(self.figure)
            except Exception:
                pass
        self.figure = None
        self.image = None
        self.image_label = None
        self._original_pil_image = None

    def get(self):
        """Return the currently embedded figure or image.

        Returns:
            Optional[Any]: Embedded figure/image, or `None` when empty.
        """
        if self.figure is not None:
            return self.figure
        elif self.image is not None:
            return self.image
        else:
            return None
        
    def set(self, value):
        """Set the content of the figure container.

        Args:
            value: `Figure`, `PhotoImage`, or image file path string.
        """
        if isinstance(value, Figure):
            self.embed_figure(value)
        elif isinstance(value, tk.PhotoImage):
            self.embed_image(value)
        elif isinstance(value, str):
            self.embed_image_file(value)
        else:
            raise ValueError("Unsupported value type for FigureContainer. Must be Figure, PhotoImage, or file path string.")


if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
    
    root = BHoMBaseWindow()
    parent_container = root.content_frame

    # Create figure container
    figure_container = FigureContainer(
        parent=parent_container, 
        item_title="Figure Container", 
        helper_text="This widget can embed matplotlib figures or images.",
        packing_options=PackingOptions(padx=10, pady=10, fill='both', expand=True)
    )
    figure_container.build()

    # Create and embed a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 4), dpi=80)
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3], marker='o')
    ax.set_title("Sample Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    figure_container.embed_figure(fig)

    root.mainloop()
