"""Checkbox selection widget with multi-select support and state helpers."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Callable

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

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
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, item_title=item_title, helper_text=helper_text, **kwargs)

		self.fields = [str(field) for field in (fields or [])]
		self.command = command
		self.orient = orient.lower()
		self.max_per_line = max_per_line
		self.value_vars = {}  # Dictionary mapping field names to BooleanVars
		self._buttons = []

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
		self.value_vars.clear()

		for index, field in enumerate(self.fields):
			var = tk.BooleanVar(value=False)
			self.value_vars[field] = var
			
			button = ttk.Label(
				self.buttons_frame,
				text=f"□ {field}",
				cursor="hand2"
			)
			getattr(self, "align_child_text")(button)
			button.bind("<Button-1>", lambda e, f=field: self._toggle_field(f))
			
			if self.max_per_line and self.max_per_line > 0:
				if self.orient == "horizontal":
					row = index // self.max_per_line
					column = index % self.max_per_line
				else:
					row = index % self.max_per_line
					column = index // self.max_per_line
				button.grid(row=row, column=column, padx=(0, 10), pady=(0, 4), sticky=getattr(self, "_grid_sticky"))
			elif self.orient == "horizontal":
				button.grid(row=0, column=index, padx=(0, 10), pady=(0, 4), sticky=getattr(self, "_grid_sticky"))
			else:
				button.grid(row=index, column=0, padx=(0, 10), pady=(0, 4), sticky=getattr(self, "_grid_sticky"))
			self._buttons.append(button)

	def _toggle_field(self, field):
		"""Toggle a field's state when clicked."""
		self.value_vars[field].set(not self.value_vars[field].get())
		self._on_select_field(field)

	def _on_select_field(self, field):
		"""Handle checkbox selection change and update visual indicator."""
		# Find the button for this field and update its text
		for button in self._buttons:
			button_text = button.cget("text")
			# Extract field name (remove the box indicator)
			current_field = button_text[2:]  # Skip "□ " or "■ "
			if current_field == field:
				if self.value_vars[field].get():
					button.configure(text=f"■ {field}")
				else:
					button.configure(text=f"□ {field}")
				break
		
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
		
		# Update visual indicators
		for button in self._buttons:
			button_text = button.cget("text")
			current_field = button_text[2:]  # Skip "□ " or "■ "
			if current_field in values:
				button.configure(text=f"■ {current_field}")
			else:
				button.configure(text=f"□ {current_field}")

	def select_all(self):
		"""Select all checkboxes."""
		for var in self.value_vars.values():
			var.set(True)
		# Update visual indicators
		for button in self._buttons:
			button_text = button.cget("text")
			field = button_text[2:]  # Skip box indicator
			button.configure(text=f"■ {field}")
		if self.command:
			self.command(self.get())

	def deselect_all(self):
		"""Deselect all checkboxes."""
		for var in self.value_vars.values():
			var.set(False)
		# Update visual indicators
		for button in self._buttons:
			button_text = button.cget("text")
			field = button_text[2:]  # Skip box indicator
			button.configure(text=f"□ {field}")
		if self.command:
			self.command(self.get())

	def toggle_all(self):
		"""Toggle all checkbox states."""
		for var in self.value_vars.values():
			var.set(not var.get())
		# Update visual indicators
		for button in self._buttons:
			button_text = button.cget("text")
			field = button_text[2:]  # Skip box indicator
			if self.value_vars[field].get():
				button.configure(text=f"■ {field}")
			else:
				button.configure(text=f"□ {field}")
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
		item_title="Choose Options",
		helper_text="Select one or more options below:",
		packing_options=PackingOptions(padx=20, pady=20)
	)
	widget.build()

	# Add control buttons for demonstration
	control_frame = ttk.Frame(parent_frame)
	control_frame.pack(padx=20, pady=10)

	ttk.Button(control_frame, text="Select All", command=widget.select_all).pack(side="left", padx=5)
	ttk.Button(control_frame, text="Deselect All", command=widget.deselect_all).pack(side="left", padx=5)
	ttk.Button(control_frame, text="Toggle All", command=widget.toggle_all).pack(side="left", padx=5)

	root.mainloop()
