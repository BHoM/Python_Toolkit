"""Spinbox widget for numeric or list-based stepped input."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Union, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget


class Spinbox(BHoMBaseWidget):
	"""A spinbox widget supporting numeric ranges or explicit value lists."""

	def __init__(
			self,
			parent,
			values: Optional[Union[List[str], List[int], List[float]]] = None,
			from_: Optional[Union[int, float]] = None,
			to: Optional[Union[int, float]] = None,
			increment: Union[int, float] = 1,
			default: Optional[Union[str, int, float]] = None,
			command: Optional[Callable[[str], None]] = None,
			width: int = 10,
			wrap: bool = False,
			**kwargs):
		"""
		Args:
			parent (tk.Widget): The parent widget.
			values (list, optional): Explicit list of string values to step through.
				If provided, ``from_``, ``to`` and ``increment`` are ignored.
			from_ (int | float, optional): Minimum value for numeric mode.
			to (int | float, optional): Maximum value for numeric mode.
			increment (int | float): Step size for numeric mode. Defaults to 1.
			default (str | int | float, optional): Initial value.
			command (callable, optional): Called with the current value (str) on change.
			width (int): Width of the entry in characters.
			wrap (bool): Whether stepping wraps around at the limits.
			item_title (str, optional): Optional header text.
			helper_text (str, optional): Optional helper text.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.command = command
		self._value_var = tk.StringVar()

		# Determine the native type for get() coercion
		if values and len(values) > 0:
			self._value_type = type(values[0])
		elif from_ is not None:
			self._value_type = type(from_)
		else:
			self._value_type = str

		spinbox_kwargs: dict = dict(
			textvariable=self._value_var,
			width=width,
			wrap=wrap,
		)

		if values:
			spinbox_kwargs["values"] = [str(v) for v in values]
		else:
			if from_ is not None:
				spinbox_kwargs["from_"] = from_
			if to is not None:
				spinbox_kwargs["to"] = to
			spinbox_kwargs["increment"] = increment

		self.spinbox = ttk.Spinbox(self.content_frame, **spinbox_kwargs)
		self.spinbox.pack(side="top", anchor=self._pack_anchor)

		self._value_var.trace_add("write", self._on_change)

		if default is not None:
			self.set(default)
		elif values:
			self._value_var.set(str(values[0]))
		elif from_ is not None:
			self._value_var.set(str(from_))

	def _on_change(self, *_):
		"""Fire the command callback when the value changes."""
		if self.command:
			self.command(self.get())

	def get(self) -> Union[str, int, float]:
		"""Return the current value cast to its original type.

		Returns:
			str | int | float: Current spinbox value in its original type.
		"""
		raw = self._value_var.get()
		try:
			return self._value_type(raw)
		except (ValueError, TypeError):
			return raw

	def get_int(self) -> int:
		"""Return the current value as an integer.

		Returns:
			int: Current spinbox value.

		Raises:
			ValueError: If the value cannot be converted to int.
		"""
		return int(self.get())

	def get_float(self) -> float:
		"""Return the current value as a float.

		Returns:
			float: Current spinbox value.

		Raises:
			ValueError: If the value cannot be converted to float.
		"""
		return float(self.get())

	def set(self, value: Union[str, int, float]):
		"""Set the spinbox value.

		Args:
			value: New value to display.
		"""
		self._value_var.set(str(value))

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
		"""Validate that the current value is non-empty.

		Returns:
			tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
				``(is_valid, message, severity)``.
		"""
		if not str(self.get()).strip():
			return getattr(self, "apply_validation")((False, "A value is required.", "error"))
		return getattr(self, "apply_validation")((True, None, None))


if __name__ == "__main__":

	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	def on_change(value):
		print(f"Value: {value}")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	# Numeric spinbox
	numeric = Spinbox(
		parent_frame,
		from_=0,
		to=100,
		increment=5,
		default=25,
		command=on_change,
		item_title="Numeric",
		helper_text="Pick a value between 0 and 100",
		build_options=PackingOptions(padx=20, pady=(20, 8)),
		width = 1,
	)
	numeric.build()

	# List-based spinbox
	list_spin = Spinbox(
		parent_frame,
		values=["Small", "Medium", "Large", "X-Large"],
		default="Medium",
		command=on_change,
		item_title="Size",
		helper_text="Step through available sizes",
		build_options=PackingOptions(padx=20, pady=(0, 20)),
		width=100
	)
	list_spin.build()

	root.mainloop()
