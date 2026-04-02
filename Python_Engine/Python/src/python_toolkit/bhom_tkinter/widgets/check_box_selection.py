"""Checkbox selection widget with multi-select support and state helpers."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Callable, Tuple, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button

class CheckboxSelection(BHoMBaseWidget):
	"""A reusable checkbox selection widget built from a list of fields, allowing multiple selections."""

	def __init__(
			self, 
			parent, 
			fields=None, 
			command: Optional[Callable[[List[str]], None]] = None, 
			defaults: Optional[List[str]] = None, 
			orient="vertical", 
			max_per_line=None, 
			item_title: Optional[str] = None, 
			helper_text: Optional[str] = None, 
			min_selections: Optional[int] = None,
			max_selections: Optional[int] = None,
			**kwargs):
		"""
		Args:
			parent (tk.Widget): The parent widget.
			fields (list, optional): List of selectable fields.
			command (callable, optional): Called with list of selected values when changed.
			defaults (list, optional): List of default selected values.
			orient (str): Either "vertical" or "horizontal".
			max_per_line (int, optional): Maximum items per row/column before wrapping.
			item_title (str, optional): Optional header text shown at the top of the widget frame.
			helper_text (str, optional): Optional helper text shown above the checkboxes.
			min_selections (int, optional): Minimum number of selections required.
			max_selections (int, optional): Maximum number of selections allowed.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, item_title=item_title, helper_text=helper_text, **kwargs)

		self.fields = [str(field) for field in (fields or [])]
		self.command = command
		self.orient = orient.lower()
		self.max_per_line = max_per_line
		self.value_vars = {}  # Dictionary mapping field names to BooleanVars
		self._buttons = []
		self._field_buttons = {}
		self.min_selections = min_selections
		self.max_selections = max_selections

		# Sub-frame for checkbox controls
		self.buttons_frame = ttk.Frame(self.content_frame)
		self.buttons_frame.pack(side="top", fill="x", expand=True)

		self._build_buttons()

		if defaults:
			self.set(defaults)

	def _build_buttons(self):
		"""Create checkboxes from current fields."""
		for button in self._buttons:
			button.destroy()
		self._buttons.clear()
		self._field_buttons.clear()
		self.value_vars.clear()

		for index, field in enumerate(self.fields):
			var = tk.BooleanVar(value=False)
			self.value_vars[field] = var

			button = ttk.Checkbutton(
				self.buttons_frame,
				text=field,
				variable=var,
				style="Checkbox.TCheckbutton",
				command=lambda f=field: self._on_select_field(f),
			)
			self.align_child_text(button)

			if self.max_per_line and self.max_per_line > 0:
				if self.orient == "horizontal":
					row = index // self.max_per_line
					column = index % self.max_per_line
				else:
					row = index % self.max_per_line
					column = index // self.max_per_line
				button.grid(row=row, column=column, padx=(0, 10), pady=(0, 4), sticky=self._grid_sticky)
			elif self.orient == "horizontal":
				button.grid(row=0, column=index, padx=(0, 10), pady=(0, 4), sticky=self._grid_sticky)
			else:
				button.grid(row=index, column=0, padx=(0, 10), pady=(0, 4), sticky=self._grid_sticky)
			self._buttons.append(button)
			self._field_buttons[field] = button

	def _on_select_field(self, field):
		"""Handle checkbox selection change."""
		if self.command:
			self.command(self.get())

	def get(self) -> List[str]:
		"""Return a list of currently selected values.

		Returns:
			List[str]: Selected field labels.
		"""
		return [field for field, var in self.value_vars.items() if var.get()]

	def set(self, value: List[str]):
		"""Set the selected values.

		Args:
			value: Field names to mark as selected.
		"""
		values = [str(v) for v in (value or [])]
		for field, var in self.value_vars.items():
			var.set(field in values)

	def select_all(self):
		"""Select all checkboxes."""
		for var in self.value_vars.values():
			var.set(True)
		if self.command:
			self.command(self.get())

	def deselect_all(self):
		"""Deselect all checkboxes."""
		for var in self.value_vars.values():
			var.set(False)
		if self.command:
			self.command(self.get())

	def toggle_all(self):
		"""Toggle all checkbox states."""
		for var in self.value_vars.values():
			var.set(not var.get())
		if self.command:
			self.command(self.get())

	def set_fields(self, fields: List[str], defaults: Optional[List[str]] = None):
		"""Replace the available fields and rebuild the widget.

		Args:
			fields: New available field names.
			defaults: Optional field names to preselect after rebuild.
		"""
		self.fields = [str(field) for field in (fields or [])]
		self._build_buttons()

		if defaults:
			self.set(defaults)

	def pack(self, **kwargs):
		"""Pack the widget with the given options.

		Args:
			**kwargs: Pack geometry manager options.
		"""
		super().pack(**kwargs)

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
		"""Validate the current selection against min/max constraints.

		Returns:
			tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
				`(is_valid, message, severity)` where severity is `None` when
				valid, or `"error"` for an invalid selection.
		"""
		selected_count = len(self.get())
		if self.min_selections is not None and selected_count < self.min_selections:
			return getattr(self, "apply_validation")((False, f"Select at least {self.min_selections} options.", "error"))
		if self.max_selections is not None and selected_count > self.max_selections:
			return getattr(self, "apply_validation")((False, f"Select no more than {self.max_selections} options.", "error"))
		return getattr(self, "apply_validation")((True, None, None))

if __name__ == "__main__":

	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	def on_selection(values):
		"""Print selected values in the standalone example."""
		print(f"Selected: {values}")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	widget = CheckboxSelection(
		parent_frame,
		fields=["Option A", "Option B", "Option C", "Option D", "Option E", "Option F", "Option G"],
		command=on_selection,
		defaults=["Option B", "Option D"],
		orient="vertical",
		max_per_line=6,
		min_selections=2,
		item_title="Choose Options",
		helper_text="Select one or more options below:",
		build_options=PackingOptions(padx=20, pady=20)
	)
	widget.build()

	# Add control buttons for demonstration
	control_frame = ttk.Frame(parent_frame)
	control_frame.pack(padx=20, pady=10)

	Button(control_frame, text="Select All", command=widget.select_all).pack(side="left", padx=5)
	Button(control_frame, text="Deselect All", command=widget.deselect_all).pack(side="left", padx=5)

	root.mainloop()
