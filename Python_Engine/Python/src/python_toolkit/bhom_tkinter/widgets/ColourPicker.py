"""Colour picker widget with themed popup and live RGB/hex preview."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

class ColourPicker(BHoMBaseWidget):
	"""A simple colour picker widget where the swatch opens a themed colour dialog."""

	def __init__(
		self,
		parent: ttk.Frame,
		default_colour: str = "#ffffff",
		swatch_width: int = 48,
		swatch_height: int = 28,
		command: Optional[Callable[[str], None]] = None,
		**kwargs,
	) -> None:
		"""
		Args:
			parent: Parent widget.
			default_colour: Initial colour value in hex format.
			swatch_width: Width of the clickable colour swatch in pixels.
			swatch_height: Height of the clickable colour swatch in pixels.
			command: Optional callback called with selected hex colour.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.command = command
		self.colour_var = tk.StringVar(value=default_colour)
		self.swatch_width = max(1, int(swatch_width))
		self.swatch_height = max(1, int(swatch_height))
		self._picker_window: Optional[tk.Toplevel] = None
		self._popup_preview: Optional[tk.Canvas] = None
		self._popup_swatch: Optional[int] = None
		self._popup_hex_var: Optional[tk.StringVar] = None
		self._popup_red_var: Optional[tk.IntVar] = None
		self._popup_green_var: Optional[tk.IntVar] = None
		self._popup_blue_var: Optional[tk.IntVar] = None

		controls = ttk.Frame(self.content_frame)
		controls.pack(side="top", anchor=getattr(self, "_pack_anchor"))

		self.preview = tk.Canvas(
			controls,
			width=self.swatch_width,
			height=self.swatch_height,
			highlightthickness=1,
			cursor="hand2",
		)
		self.preview.pack()
		self._swatch = self.preview.create_rectangle(0, 0, self.swatch_width, self.swatch_height, outline="#666666")
		self.preview.bind("<Button-1>", lambda _event: self._select_colour())

		self._update_preview(default_colour)

	def _select_colour(self) -> None:
		"""Open the themed colour picker popup."""
		if self._picker_window and self._picker_window.winfo_exists():
			self._picker_window.focus_force()
			return

		current_colour = self.get()
		red, green, blue = self._hex_to_rgb(current_colour)

		root_window = self.winfo_toplevel()
		window = tk.Toplevel(root_window)
		window.title("Select Colour")
		window.transient(root_window)
		window.resizable(False, False)
		window.protocol("WM_DELETE_WINDOW", self._close_picker)

		self._picker_window = window
		self._popup_red_var = tk.IntVar(value=red)
		self._popup_green_var = tk.IntVar(value=green)
		self._popup_blue_var = tk.IntVar(value=blue)
		self._popup_hex_var = tk.StringVar(value=current_colour)

		container = ttk.Frame(window, padding=10)
		container.pack(fill=tk.BOTH, expand=True)

		self._build_slider_row(container, "R", self._popup_red_var, 0)
		self._build_slider_row(container, "G", self._popup_green_var, 1)
		self._build_slider_row(container, "B", self._popup_blue_var, 2)

		hex_row = ttk.Frame(container)
		hex_row.grid(row=3, column=0, sticky="ew", pady=(8, 4))
		ttk.Label(hex_row, text="Hex").pack(side=tk.LEFT)
		hex_entry = ttk.Entry(hex_row, textvariable=self._popup_hex_var, width=10)
		hex_entry.pack(side=tk.LEFT, padx=(8, 0))
		hex_entry.bind("<Return>", lambda _event: self._on_hex_entered())

		preview_row = ttk.Frame(container)
		preview_row.grid(row=4, column=0, sticky="w", pady=(4, 8))
		ttk.Label(preview_row, text="Preview").pack(side=tk.LEFT)
		self._popup_preview = tk.Canvas(preview_row, width=48, height=28, highlightthickness=1)
		self._popup_preview.pack(side=tk.LEFT, padx=(8, 0))
		self._popup_swatch = self._popup_preview.create_rectangle(0, 0, 48, 28, outline="#666666")

		button_row = ttk.Frame(container)
		button_row.grid(row=5, column=0, sticky="e")
		ttk.Button(button_row, text="Cancel", command=self._close_picker).pack(side=tk.LEFT, padx=(0, 6))
		ttk.Button(button_row, text="Apply", command=self._apply_popup_colour).pack(side=tk.LEFT)

		container.columnconfigure(0, weight=1)

		self._on_rgb_changed()
		window.grab_set()
		hex_entry.focus_set()

	def _update_preview(self, colour: str) -> None:
		"""Render the selected colour in the preview swatch."""
		self.preview.itemconfig(self._swatch, fill=colour)

	def _build_slider_row(self, parent: ttk.Frame, label_text: str, value_var: tk.IntVar, row: int) -> None:
		row_frame = ttk.Frame(parent)
		row_frame.grid(row=row, column=0, sticky="ew", pady=2)

		ttk.Label(row_frame, text=label_text).pack(side=tk.LEFT)
		slider = ttk.Scale(
			row_frame,
			from_=0,
			to=255,
			orient=tk.HORIZONTAL,
			style="ColourPicker.Horizontal.TScale",
			command=lambda value, var=value_var: self._on_slider_move(var, value),
		)
		slider.set(value_var.get())
		slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
		value_label = ttk.Label(row_frame, textvariable=value_var, width=4, anchor="e")
		value_label.pack(side=tk.LEFT)

	def _on_slider_move(self, value_var: tk.IntVar, value: str) -> None:
		value_var.set(int(float(value)))
		self._on_rgb_changed()

	def _on_rgb_changed(self) -> None:
		if not (self._popup_red_var and self._popup_green_var and self._popup_blue_var and self._popup_hex_var):
			return

		colour = self._rgb_to_hex(self._popup_red_var.get(), self._popup_green_var.get(), self._popup_blue_var.get())
		self._popup_hex_var.set(colour)
		self._update_popup_preview(colour)

	def _on_hex_entered(self) -> None:
		if not self._popup_hex_var:
			return

		red, green, blue = self._hex_to_rgb(self._popup_hex_var.get())
		if self._popup_red_var and self._popup_green_var and self._popup_blue_var:
			self._popup_red_var.set(red)
			self._popup_green_var.set(green)
			self._popup_blue_var.set(blue)
		self._popup_hex_var.set(self._rgb_to_hex(red, green, blue))
		self._update_popup_preview(self._popup_hex_var.get())

	def _update_popup_preview(self, colour: str) -> None:
		if self._popup_preview and self._popup_swatch is not None:
			self._popup_preview.itemconfig(self._popup_swatch, fill=colour)

	def _apply_popup_colour(self) -> None:
		if not self._popup_hex_var:
			return

		selected = self._rgb_to_hex(*self._hex_to_rgb(self._popup_hex_var.get()))
		self.set(selected)
		if self.command:
			self.command(selected)
		self._close_picker()

	def _close_picker(self) -> None:
		if self._picker_window and self._picker_window.winfo_exists():
			try:
				self._picker_window.grab_release()
			except tk.TclError:
				pass
			self._picker_window.destroy()

		self._picker_window = None
		self._popup_preview = None
		self._popup_swatch = None
		self._popup_hex_var = None
		self._popup_red_var = None
		self._popup_green_var = None
		self._popup_blue_var = None

	@staticmethod
	def _rgb_to_hex(red: int, green: int, blue: int) -> str:
		red = max(0, min(255, int(red)))
		green = max(0, min(255, int(green)))
		blue = max(0, min(255, int(blue)))
		return f"#{red:02x}{green:02x}{blue:02x}"

	@staticmethod
	def _hex_to_rgb(colour: str) -> tuple[int, int, int]:
		value = (colour or "").strip().lstrip("#")
		if len(value) == 3:
			value = "".join(ch * 2 for ch in value)
		if len(value) != 6:
			return 255, 255, 255
		try:
			return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
		except ValueError:
			return 255, 255, 255

	def get(self) -> str:
		"""Return the currently selected hex colour.

		Returns:
			str: Selected colour in hex format.
		"""
		return self.colour_var.get()

	def set(self, value: str) -> None:
		"""Set the current colour and refresh the preview swatch.

		Args:
			value: Colour value in hex format.
		"""
		self.colour_var.set(value)
		self._update_preview(value)


if __name__ == "__main__":
	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	root = BHoMBaseWindow()
	parent_container = root.content_frame

	def on_colour_changed(colour: str) -> None:
		"""Print selected colour in the standalone example."""
		print(f"Selected colour: {colour}")

	colour_picker = ColourPicker(
		parent_container,
		command=on_colour_changed,
		item_title="Colour Picker",
		helper_text="Pick a colour for plotting.",
		alignment="center",
		packing_options=PackingOptions(padx=10, pady=10),
	)
	colour_picker.build()

	root.mainloop()
