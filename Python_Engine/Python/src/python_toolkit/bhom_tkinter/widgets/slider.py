"""Horizontal slider widget with a linked editable value display."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget


class Slider(BHoMBaseWidget):
	"""A horizontal slider (ttk.Scale) with a linked editable numeric entry."""

	def __init__(
		self,
		parent,
		from_: float = 0.0,
		to: float = 1.0,
		default: float = 0.0,
		resolution: float = 0.01,
		show_value: bool = True,
		value_width: int = 5,
		command: Optional[Callable[[float], None]] = None,
		**kwargs,
	) -> None:
		"""
		Args:
			parent: Parent widget.
			from_: Minimum slider value.
			to: Maximum slider value.
			default: Initial value.
			resolution: Snap increment. Set to 0 to disable snapping.
			show_value: When True, an editable entry is shown beside the slider.
			value_width: Character width of the value entry.
			command: Callback invoked with the current float value on every change.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.from_ = float(from_)
		self.to = float(to)
		self.resolution = float(resolution)
		self.command = command

		self._var = tk.DoubleVar(value=self._snap(float(default)))

		row = ttk.Frame(self.content_frame)
		row.pack(side="top", fill="x")

		self._scale = ttk.Scale(
			row,
			from_=self.from_,
			to=self.to,
			orient=tk.HORIZONTAL,
			variable=self._var,
			command=self._on_scale_move,
		)
		self._scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

		if show_value:
			self._display_var = tk.StringVar(value=f"{self._snap(float(default)):.2f}")
			self._value_entry = ttk.Entry(row, textvariable=self._display_var, width=value_width)
			self._value_entry.pack(side=tk.LEFT, padx=(4, 0))
			self._value_entry.bind("<Return>", self._on_entry_changed)
			self._value_entry.bind("<FocusOut>", self._on_entry_changed)
		else:
			self._display_var = None
			self._value_entry = None

	# ------------------------------------------------------------------
	# Event handlers
	# ------------------------------------------------------------------

	def _on_scale_move(self, raw: str) -> None:
		"""Called by ttk.Scale when the slider moves."""
		value = self._snap(float(raw))
		self._var.set(value)
		if self._display_var is not None:
			self._display_var.set(f"{value:.2f}")
		if self.command:
			self.command(value)
		self._fire_on_change(value)

	def _on_entry_changed(self, _event=None) -> None:
		"""Called when the user edits the value entry."""
		if self._display_var is None:
			return
		try:
			value = float(self._display_var.get())
		except ValueError:
			value = self.get()
		value = self._snap(max(self.from_, min(self.to, value)))
		self._var.set(value)
		self._display_var.set(f"{value:.2f}")
		if self.command:
			self.command(value)
		self._fire_on_change(value)

	# ------------------------------------------------------------------
	# Helpers
	# ------------------------------------------------------------------

	def _snap(self, value: float) -> float:
		"""Snap a value to the nearest resolution step."""
		if self.resolution <= 0:
			return value
		snapped = round(round(value / self.resolution) * self.resolution, 10)
		return max(self.from_, min(self.to, snapped))

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def disable(self) -> None:
		"""Disable the slider and entry (for locked colour stops)."""
		self._scale.configure(state="disabled")
		if self._value_entry:
			self._value_entry.configure(state="disabled")

	def enable(self) -> None:
		"""Re-enable the slider and entry."""
		self._scale.configure(state="normal")
		if self._value_entry:
			self._value_entry.configure(state="normal")

	def get(self) -> float:
		"""Return the current slider value as a float.

		Returns:
			float: Current value, snapped to resolution.
		"""
		return self._snap(self._var.get())

	def set(self, value: float) -> None:
		"""Set the slider position.

		Args:
			value: New value, clamped to [from\\_, to].
		"""
		value = self._snap(max(self.from_, min(self.to, float(value))))
		self._var.set(value)
		if self._display_var is not None:
			self._display_var.set(f"{value:.2f}")

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal["info", "warning", "error"]]]:
		v = self.get()
		if v < self.from_ or v > self.to:
			return self.apply_validation(
				(False, f"Value must be between {self.from_} and {self.to}.", "error")
			)
		return self.apply_validation((True, None, None))


if __name__ == "__main__":
	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	root = BHoMBaseWindow(title="Slider Test")

	slider = Slider(
		root.content_frame,
		from_=0.0, to=1.0, default=0.5, resolution=0.01,
		item_title="Position",
		command=lambda v: print(f"Value: {v:.2f}"),
		build_options=PackingOptions(side="top", fill="x", padx=20, pady=20),
	)
	root.widgets.append(slider)
	root.build()
	root.mainloop()
