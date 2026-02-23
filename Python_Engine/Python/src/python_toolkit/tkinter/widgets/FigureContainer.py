import tkinter as tk
from tkinter import ttk
from typing import Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class FigureContainer(tk.Frame):
    """
    A reusable widget for embedding matplotlib figures and images.
    """

    def __init__(
        self,
        parent,
        item_title: Optional[str] = None,
        helper_text: Optional[str] = None,
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
        self.image: Optional[tk.PhotoImage] = None
        self.image_file: Optional[str] = None

        self.item_title = item_title
        self.helper_text = helper_text

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Header.TLabel")
            self.title_label.pack(side="top", anchor="w")

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
            self.helper_label.pack(side="top", anchor="w")

        # Container frame for embedded content (not title/helper)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="top", fill=tk.BOTH, expand=True)

        self.canvas = None
        self.image_label = None

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

        """ add matplotlib figure to the container, replacing any existing content. 
        
        Args:
            figure: Matplotlib Figure object to embed
        """

        self._clear_children()

        self.figure = figure
        self.canvas = FigureCanvasTkAgg(figure, master=self.content_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def embed_image(self, image: tk.PhotoImage) -> None:
        """
        Embed a Tk image in the figure container.

        Args:
            image: Tk PhotoImage object to embed
        """
        self._clear_children()

        self.image = image
        
        # Create label to display the image
        self.image_label = ttk.Label(self.content_frame, image=image)
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def embed_image_file(self, file_path: str) -> None:
        """
        Load and embed an image file supported by Tk PhotoImage.

        Args:
            file_path: Path to image file
        """
        image = tk.PhotoImage(file=file_path)
        self.image_file = file_path
        self.embed_image(image)

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


if __name__ == "__main__":

    from python_toolkit.tkinter.DefaultRoot import DefaultRoot
    root = DefaultRoot()
    parent_container = root.content_frame

    # Create figure container
    figure_container = FigureContainer(parent=parent_container, item_title="Figure Container", helper_text="This widget can embed matplotlib figures or images.")
    figure_container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create and embed a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 4), dpi=80)
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3], marker='o')
    ax.set_title("Sample Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    figure_container.embed_figure(fig)

    root.mainloop()
