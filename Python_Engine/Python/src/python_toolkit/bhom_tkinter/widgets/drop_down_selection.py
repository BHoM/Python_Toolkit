"""Dropdown selection widget built from ttk.Combobox."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

class DropDownSelection(BHoMBaseWidget):
	"""A reusable dropdown selection widget built from a list of options."""

	def __init__(
			self, 
			parent, 
			options: Optional[List[str]] = None,
			command: Optional[Callable[[str], None]] = None,
			default: Optional[str] = None,
			width: int = 20,
			state: str = "readonly",
			**kwargs):
		"""
		Args:
			parent (tk.Widget): The parent widget.
			options (list, optional): List of selectable options.
			command (callable, optional): Called with selected value when changed.
			default (str, optional): Default selected value.
			width (int): Width of the dropdown widget in characters.
			state (str): Combobox state ("normal", "readonly", or "disabled").
			item_title (str, optional): Optional header text shown at the top of the widget frame.
			helper_text (str, optional): Optional helper text shown above the dropdown.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.options = [str(option) for option in (options or [])]
		self.command = command
		self.value_var = tk.StringVar()

		# Create the combobox in the content frame
		self.combobox = ttk.Combobox(
			self.content_frame,
			textvariable=self.value_var,
			values=self.options,
			width=width,
			state=state
		)
		self.combobox.pack(side="top", anchor=getattr(self, "_pack_anchor"), fill="x")

		# Bind selection event
		self.combobox.bind("<<ComboboxSelected>>", self._on_select)

		# Set default value
		if default is not None and default in self.options:
			self.set(default)
		elif self.options:
			self.value_var.set(self.options[0])

	def _on_select(self, event=None):
		"""Handle selection change event.

		Args:
			event: Tkinter event (optional).
		"""
		if self.command:
			self.command(self.get())

	def get(self) -> str:
		"""Return the currently selected value.

		Returns:
			str: Selected option value.
		"""
		return self.value_var.get()

	def set(self, value: str):
		"""Set the selected value.

		Args:
			value: Option value to select.
		"""
		if value in self.options:
			self.value_var.set(value)
		else:
			raise ValueError(f"Value '{value}' not in available options: {self.options}")

	def set_options(self, options: List[str], default: Optional[str] = None):
		"""Replace the available options and optionally set a new default.

		Args:
			options: New list of selectable options.
			default: Optional value to select after updating options.
		"""
		self.options = [str(option) for option in (options or [])]
		self.combobox['values'] = self.options

		if default is not None and default in self.options:
			self.set(default)
		elif self.options:
			self.value_var.set(self.options[0])
		else:
			self.value_var.set("")

	def get_selected_index(self) -> int:
		"""Return the index of the currently selected option.

		Returns:
			int: Index of selected option, or -1 if not found.
		"""
		try:
			return self.options.index(self.get())
		except ValueError:
			return -1
		
	def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
		"""Validate the current selection.

		Returns:
			tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
				`(is_valid, message, severity)` where severity is `None` when
				valid, or `"error"` for an invalid selection.
		"""
		selected = self.get()
		if not selected:
			return getattr(self, "apply_validation")((False, "No option selected.", "error"))
		if selected not in self.options:
			return getattr(self, "apply_validation")((False, f"Selected option '{selected}' is not available.", "error"))
		return getattr(self, "apply_validation")((True, None, None))

if __name__ == "__main__":

	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	def on_selection(value):
		"""Print selected value in the standalone example."""
		print(f"Selected: {value}")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	widget = DropDownSelection(
		parent_frame,
		options=["Option A", "Option B", "Option C", "Option D", "Option E"],
		command=on_selection,
		default="Option C",
		width=30,
		item_title="Choose an Option",
		helper_text="Select one option from the dropdown list.",
		alignment="center",
		build_options=PackingOptions(padx=20, pady=20)
	)
	widget.build()

	root.mainloop()
