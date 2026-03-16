"""Single-select radio-style widget built from ttk Radiobuttons."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

class RadioSelection(BHoMBaseWidget):
	"""A reusable radio selection widget built from a list of fields."""

	def __init__(
			self, 
			parent, 
			fields=None, 
			command=None, 
			default=None, 
			orient="vertical", 
			options_fill_extents: bool = False,
			max_per_line=None, 
			**kwargs):
		"""
		Args:
			parent (tk.Widget): The parent widget.
			fields (list, optional): List of selectable fields.
			command (callable, optional): Called with selected value when changed.
			default (str, optional): Default selected value.
			orient (str): Either "vertical" or "horizontal".
			options_fill_extents (bool): If `True`, radio option rows expand to
				fill their available width in the options frame.
			max_per_line (int, optional): Maximum items per row/column before wrapping.
			item_title (str, optional): Optional header text shown at the top of the widget frame.
			helper_text (str, optional): Optional helper text shown above the entry box.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.fields = [str(field) for field in (fields or [])]
		self.command = command
		self.orient = orient.lower()
		self.options_fill_extents = self._normalise_bool(options_fill_extents)
		self.max_per_line = max_per_line
		self.value_var = tk.StringVar()
		self._buttons = []

		# Sub-frame for radio button controls
		self.buttons_frame = ttk.Frame(self.content_frame)
		self.buttons_frame.pack(side="top", fill="x", expand=True)

		self._build_buttons()

		if default is not None:
			self.set(default)
		elif self.fields:
			self.value_var.set(self.fields[0])

	def _build_buttons(self):
		"""Create radio buttons from current fields."""
		for button in self._buttons:
			button.destroy()
		self._buttons.clear()
		for index in range(self.buttons_frame.grid_size()[0] + 1):
			self.buttons_frame.grid_columnconfigure(index, weight=0)

		for index, field in enumerate(self.fields):
			sticky = self._grid_sticky
			button = ttk.Radiobutton(
				self.buttons_frame,
				text=field,
				variable=self.value_var,
				value=field,
				style="Radio.TRadiobutton",
				command=lambda f=field: self._select_field(f),
			)
			self.align_child_text(button)

			if self.max_per_line and self.max_per_line > 0:
				if self.orient == "horizontal":
					row = index // self.max_per_line
					column = index % self.max_per_line
				else:
					row = index % self.max_per_line
					column = index // self.max_per_line
				button.grid(
					row=row,
					column=column,
					padx=(0, 10),
					pady=(0, 4),
					sticky=("ew" if self.options_fill_extents else sticky),
				)
				if self.options_fill_extents:
					self.buttons_frame.grid_columnconfigure(column, weight=1)
			elif self.orient == "horizontal":
				button.grid(
					row=0,
					column=index,
					padx=(0, 10),
					pady=(0, 4),
					sticky=("ew" if self.options_fill_extents else sticky),
				)
				if self.options_fill_extents:
					self.buttons_frame.grid_columnconfigure(index, weight=1)
			else:
				button.grid(
					row=index,
					column=0,
					padx=(0, 10),
					pady=(0, 4),
					sticky=("ew" if self.options_fill_extents else sticky),
				)
				if self.options_fill_extents:
					self.buttons_frame.grid_columnconfigure(0, weight=1)
			self._buttons.append(button)

	def _select_field(self, field):
		"""Handle radio button selection."""
		if self.command:
			self.command(self.get())

	def get(self):
		"""Return the currently selected value.

		Returns:
			str: Currently selected field label.
		"""
		return self.value_var.get()

	def set(self, value):
		"""Set the selected value if it exists in fields.

		Args:
			value: Field label to select.
		"""
		value = str(value)
		if value in self.fields:
			self.value_var.set(value)

	def set_fields(self, fields, default=None):
		"""Replace the available fields and rebuild the widget.

		Args:
			fields: New available field names.
			default: Optional default field to select.
		"""
		self.fields = [str(field) for field in (fields or [])]
		self._build_buttons()

		if default is not None:
			self.set(default)
		elif self.fields:
			self.value_var.set(self.fields[0])
		else:
			self.value_var.set("")

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
		"""Validate the currently selected radio option.

		Returns:
			tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
				`(is_valid, message, severity)` where severity is `None` when
				valid, or `"error"` for an invalid selection.
		"""
		selected = self.get()
		if not selected:
			return self.apply_validation((False, "No option selected.", "error"))
		if selected not in self.fields:
			return self.apply_validation((False, f"Selected option '{selected}' is not available.", "error"))
		return self.apply_validation((True, None, None))


if __name__ == "__main__":

	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	def on_selection(value):
		"""Print selected option in the standalone example."""
		print(f"Selected: {value}")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	widget = RadioSelection(
		parent_frame,
		fields=["Option A", "Option B", "Option C"],
		command=on_selection,
		default="Option B",
		alignment="center",
		options_fill_extents=True,
		orient="horizontal",
		max_per_line=3,
		item_title="Choose an Option",
		helper_text="Select one of the options below:",
		build_options=PackingOptions(pady=20)
	)
	widget.build()

	root.mainloop()
