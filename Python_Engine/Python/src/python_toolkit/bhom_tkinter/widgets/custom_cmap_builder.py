from tkinter import ttk
from typing import Callable, Iterable, Literal, Optional

from matplotlib.colors import Colormap

from python_toolkit.bhom.custom_cmaps import _as_colormap
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.windows.colour_scale_builder import ColourScaleBuilder
from python_toolkit.plot.colour_scales import ColourScale


class CmapBuilder(BHoMBaseWidget):
	"""A button that opens the ColourScaleBuilder window and reports the saved scale as a colormap."""

	def __init__(
		self,
		parent: ttk.Frame,
		data: Optional[Iterable] = None,
		units: Optional[str] = None,
		command: Optional[Callable[[Colormap, tuple], None]] = None,
		**kwargs,
	) -> None:
		"""
		Args:
			parent: Parent widget.
			data: Values the scale will colour; the builder suggests bands from them.
			units: Units of the data, stored with the scale.
			command: Called with (colormap, (vmin, vmax)) when a scale is saved.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.command = command
		self.data = data
		self.units = units
		self._last_scale: Optional[ColourScale] = None
		self._last_cmap: Optional[Colormap] = None
		self._last_bounds: tuple[float, float] = (0.0, 1.0)

		self.builder_button = Button(
			self.content_frame,
			text="Add new Colour Collection",
			command=self._open_builder,
		)
		self.builder_button.pack(side="top", fill="x")

	def _open_builder(self) -> None:
		"""Open the builder window; returns once it is closed."""
		builder = ColourScaleBuilder(self.winfo_toplevel(), data=self.data, units=self.units, on_save=self._on_saved)
		builder.run()

	def _on_saved(self, scale: ColourScale) -> None:
		self._last_scale = scale
		self._last_cmap, self._last_bounds = _as_colormap(scale)
		if self.command is not None:
			self.command(self._last_cmap, self._last_bounds)
		self._fire_on_change(self._last_cmap)

	# ------------------------------------------------------------------
	# BHoMBaseWidget interface
	# ------------------------------------------------------------------

	def get(self) -> Optional[Colormap]:
		"""Return the last saved colormap, or None if none has been built."""
		return self._last_cmap

	def get_bounds(self) -> tuple[float, float]:
		"""Return the (vmin, vmax) range of the last saved colormap."""
		return self._last_bounds

	def get_scale(self) -> Optional[ColourScale]:
		"""Return the last saved ColourScale (thresholds, labels and set included)."""
		return self._last_scale

	def set(self, value: Colormap) -> None:
		"""Store a colormap as the current result."""
		self._last_cmap = value

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal["info", "warning", "error"]]]:
		if self._last_cmap is None:
			return self.apply_validation((False, "No colormap has been built yet.", "error"))
		return self.apply_validation((True, None, None))


if __name__ == "__main__":
	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	root = BHoMBaseWindow()
	builder = CmapBuilder(root.content_frame, build_options=PackingOptions(padx=10, pady=10))
	builder.build()
	root.mainloop()
