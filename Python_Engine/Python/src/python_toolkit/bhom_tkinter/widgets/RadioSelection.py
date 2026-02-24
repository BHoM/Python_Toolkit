import tkinter as tk
from tkinter import ttk
from typing import Optional

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
			max_per_line=None, 
			**kwargs):
		"""
		Args:
			parent (tk.Widget): The parent widget.
			fields (list, optional): List of selectable fields.
			command (callable, optional): Called with selected value when changed.
			default (str, optional): Default selected value.
			orient (str): Either "vertical" or "horizontal".
			max_per_line (int, optional): Maximum items per row/column before wrapping.
			item_title (str, optional): Optional header text shown at the top of the widget frame.
			helper_text (str, optional): Optional helper text shown above the entry box.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.fields = [str(field) for field in (fields or [])]
		self.command = command
		self.orient = orient.lower()
		self.max_per_line = max_per_line
		self.value_var = tk.StringVar()
		self._buttons = []

		# Sub-frame for radio button controls
		self.buttons_frame = ttk.Frame(self)
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

		for index, field in enumerate(self.fields):
			button = ttk.Label(
				self.buttons_frame,
				text=f"○ {field}",
				cursor="hand2"
			)
			button.bind("<Button-1>", lambda _event, f=field: self._select_field(f))
			if self.max_per_line and self.max_per_line > 0:
				if self.orient == "horizontal":
					row = index // self.max_per_line
					column = index % self.max_per_line
				else:
					row = index % self.max_per_line
					column = index // self.max_per_line
				button.grid(row=row, column=column, padx=(0, 10), pady=(0, 4), sticky="w")
			elif self.orient == "horizontal":
				button.grid(row=0, column=index, padx=(0, 10), pady=(0, 4), sticky="w")
			else:
				button.grid(row=index, column=0, padx=(0, 10), pady=(0, 4), sticky="w")
			self._buttons.append(button)

		self._update_visual_state()

	def _select_field(self, field):
		"""Select a field when clicked."""
		self.value_var.set(field)
		self._update_visual_state()
		if self.command:
			self.command(self.get())

	def _update_visual_state(self):
		"""Update visual indicators for all buttons."""
		selected_value = self.value_var.get()
		for button in self._buttons:
			button_text = button.cget("text")
			current_field = button_text[2:]
			if current_field == selected_value:
				button.configure(text=f"● {current_field}")
			else:
				button.configure(text=f"○ {current_field}")

	def get(self):
		"""Return the currently selected value."""
		return self.value_var.get()

	def set(self, value):
		"""Set the selected value if it exists in fields."""
		value = str(value)
		if value in self.fields:
			self.value_var.set(value)
			self._update_visual_state()

	def set_fields(self, fields, default=None):
		"""Replace the available fields and rebuild the widget."""
		self.fields = [str(field) for field in (fields or [])]
		self._build_buttons()

		if default is not None:
			self.set(default)
		elif self.fields:
			self.value_var.set(self.fields[0])
		else:
			self.value_var.set("")


if __name__ == "__main__":

	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

	def on_selection(value):
		print(f"Selected: {value}")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	widget = RadioSelection(
		parent_frame,
		fields=["Option A", "Option B", "Option C", "Option D", "Option E", "Option F", "Option G"],
		command=on_selection,
		default="Option B",
		orient="vertical",
		max_per_line=6,
		item_title="Choose an Option",
		helper_text="Select one of the options below:"
	)
	widget.pack(padx=20, pady=20)

	root.mainloop()
