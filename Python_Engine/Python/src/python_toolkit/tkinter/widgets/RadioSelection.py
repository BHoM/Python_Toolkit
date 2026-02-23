import tkinter as tk
from tkinter import ttk
from typing import Optional

class RadioSelection(tk.Frame):
	"""A reusable radio selection widget built from a list of fields."""

	def __init__(self, parent, fields=None, command=None, default=None, orient="vertical", max_per_line=None, item_title: Optional[str] = None, helper_text: Optional[str] = None, **kwargs):
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
		self.item_title = item_title
		self.helper_text = helper_text
		self.value_var = tk.StringVar()
		self._buttons = []

		# Optional header/title label at the top of the widget
		if self.item_title:
			self.title_label = ttk.Label(self, text=self.item_title, style="Header.TLabel")
			self.title_label.pack(side="top", anchor="w")

		# Optional helper/requirements label above the input
		if self.helper_text:
			self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
			self.helper_label.pack(side="top", anchor="w")

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
			button = ttk.Radiobutton(
				self.buttons_frame,
				text=field,
				value=field,
				variable=self.value_var,
				command=self._on_select,
			)
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

	def _on_select(self):
		"""Handle option selection."""
		if self.command:
			self.command(self.get())

	def get(self):
		"""Return the currently selected value."""
		return self.value_var.get()

	def set(self, value):
		"""Set the selected value if it exists in fields."""
		value = str(value)
		if value in self.fields:
			self.value_var.set(value)

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

	from python_toolkit.tkinter.DefaultRoot import DefaultRoot

	def on_selection(value):
		print(f"Selected: {value}")

	root = DefaultRoot()
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
