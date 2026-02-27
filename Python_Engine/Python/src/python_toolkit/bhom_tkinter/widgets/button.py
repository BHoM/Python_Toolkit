"""Simple button widget with action callback following BHoM toolkit patterns."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget


class Button(BHoMBaseWidget):
	"""A minimal button widget that invokes a callback when clicked.

	- `get()` returns the number of times the button has been clicked.
	- `set()` can update the button label when passed a string.
	"""

	def __init__(
		self,
		parent,
		text: str = "Click",
		command: Optional[Callable[[], None]] = None,
		width: int = 25,
		style: Optional[str] = None,
		**kwargs,
	):
		super().__init__(parent, **kwargs)

		self._click_count = 0
		self._user_command = command

		self.button = ttk.Button(
			self.content_frame,
			text=text,
			command=self._on_click,
			width=width,
			style=style,
		)
		self.button.pack(side="top", anchor=getattr(self, "_pack_anchor"))

	def _on_click(self):
		"""Internal click handler increments counter and calls user callback."""
		self._click_count += 1
		if self._user_command:
			try:
				self._user_command()
			except Exception:
				# Keep widget robust; do not propagate callback errors
				pass

	def get(self) -> int:
		"""Return the number of clicks recorded."""
		return self._click_count

	def set(self, value):
		"""If given a string, set the button's label; otherwise ignore."""
		if isinstance(value, str):
			self.button.configure(text=value)

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
		"""Button has no user-editable state, so validation is always valid unless overridden."""
		return self.apply_validation((True, None, None))


if __name__ == "__main__":
	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	def demo_action():
		print("Button pressed!")

	root = BHoMBaseWindow()
	parent_frame = root.content_frame

	widget = Button(
		parent_frame,
		text="Press me",
		command=demo_action,
		item_title="Demo Button",
		helper_text="A minimal clickable button.",
		packing_options=PackingOptions(anchor="w", padx=20, pady=20),
		alignment="center",
	)
	widget.build()

	root.mainloop()

