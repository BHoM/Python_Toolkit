import tkinter as tk
from tkinter import ttk
from typing import Optional
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class FigureContainer(ttk.Frame):
    """
    A reusable widget for embedding matplotlib figures and images.
    """

    def __init__(
        self,
        parent: tk.Widget,
        **kwargs
    ) -> None:
        """
        Initialize the FigureContainer widget.

        Args:
            parent: Parent widget
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.figure: Optional[Figure] = None
        self.figure_canvas: Optional[FigureCanvasTkAgg] = None
        self.image: Optional[tk.PhotoImage] = None
        self.image_label: Optional[ttk.Label] = None

    def _clear_children(self) -> None:
        """Destroy any child widgets hosted by this frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def embed_figure(self, figure: Figure) -> None:
        """
        Embed a matplotlib figure in the figure container.

        Args:
            figure: Matplotlib Figure object to embed
        """
        self._clear_children()

        self.figure = figure
        self.figure_canvas = FigureCanvasTkAgg(figure, master=self)
        self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.figure_canvas.draw()
        self.image = None
        self.image_label = None

    def embed_image(self, image: tk.PhotoImage) -> None:
        """
        Embed a Tk image in the figure container.

        Args:
            image: Tk PhotoImage object to embed
        """
        self._clear_children()

        self.image = image
        self.image_label = ttk.Label(self, image=image)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.figure = None
        self.figure_canvas = None

    def embed_image_file(self, file_path: str) -> None:
        """
        Load and embed an image file supported by Tk PhotoImage.

        Args:
            file_path: Path to image file
        """
        image = tk.PhotoImage(file=file_path)
        self.embed_image(image)

    def clear(self) -> None:
        """Clear the figure container."""
        self._clear_children()
        self.figure = None
        self.figure_canvas = None
        self.image = None
        self.image_label = None


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    root = tk.Tk()
    root.title("Figure Container Test")
    root.geometry("500x400")

    # Create figure container
    figure_container = FigureContainer(root)
    figure_container.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create and embed a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 4), dpi=80)
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3], marker='o')
    ax.set_title("Sample Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    figure_container.embed_figure(fig)

    root.mainloop()
