"""Lightweight themed Toplevel popup window without the BHoM banner."""

import ctypes
import platform
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class BHoMBasePopup(tk.Toplevel):
	"""
	A lightweight themed popup window for transient interactions.

	Unlike BHoMBaseWindow it has no branded banner and is intended for quick,
	modal (or non-modal) popups such as colour pickers, confirmations, and
	inline editors.  The active ttk theme is inherited automatically from the
	root Tk window.
	"""

	def __init__(
		self,
		parent: tk.Misc,
		title: str = "",
		modal: bool = True,
		resizable: bool = False,
		on_close: Optional[Callable] = None,
		center_on_parent: bool = True,
		padding: int = 10,
		**kwargs,
	) -> None:
		"""
		Args:
			parent: Parent widget. The popup is made transient to the root window.
			title: Window title text.
			modal: Whether the popup grabs input focus and blocks the parent.
			resizable: Whether the window can be resized by the user.
			on_close: Optional callback invoked *after* the popup is destroyed.
			center_on_parent: Centre the popup over the parent root window.
			padding: Padding applied to the content frame.
			**kwargs: Additional Toplevel options.
		"""
		root = parent.winfo_toplevel()
		super().__init__(root, **kwargs)

		self._parent = parent
		self._on_close_callback = on_close
		self._modal = modal
		self._should_center = center_on_parent

		self.title(title)
		self.transient(root)
		self.resizable(resizable, resizable)
		self.protocol("WM_DELETE_WINDOW", self.close)

		self.content_frame = ttk.Frame(self, padding=padding)
		self.content_frame.pack(fill=tk.BOTH, expand=True)

	# ------------------------------------------------------------------
	# Public API
	# ------------------------------------------------------------------

	def show(self, focus_widget: Optional[tk.Widget] = None) -> None:
		"""Finalise the popup: size, position, theme, and grab input.

		Call this *after* all content has been added to ``content_frame``.

		Args:
			focus_widget: Widget that receives keyboard focus on open.
		"""
		self.update_idletasks()

		if self._should_center:
			self._center_on_parent_window()

		self._set_titlebar_theme()

		if self._modal:
			self.grab_set()

		if focus_widget is not None:
			focus_widget.focus_set()

	def close(self) -> None:
		"""Destroy the popup and invoke the on_close callback (if any)."""
		if self.winfo_exists():
			try:
				if self._modal:
					self.grab_release()
			except tk.TclError:
				pass
			self.destroy()

		if self._on_close_callback:
			self._on_close_callback()

	# ------------------------------------------------------------------
	# Internals
	# ------------------------------------------------------------------

	def _center_on_parent_window(self) -> None:
		"""Position the popup centred over its parent's root window."""
		root = self._parent.winfo_toplevel()
		self.update_idletasks()

		popup_width = self.winfo_reqwidth()
		popup_height = self.winfo_reqheight()

		parent_x = root.winfo_rootx()
		parent_y = root.winfo_rooty()
		parent_width = root.winfo_width()
		parent_height = root.winfo_height()

		x = parent_x + (parent_width - popup_width) // 2
		y = parent_y + (parent_height - popup_height) // 2

		# Clamp to screen bounds so the popup is always fully visible.
		screen_width = self.winfo_screenwidth()
		screen_height = self.winfo_screenheight()
		x = max(0, min(x, screen_width - popup_width))
		y = max(0, min(y, screen_height - popup_height))

		self.geometry(f"+{x}+{y}")

	def _set_titlebar_theme(self) -> None:
		"""Apply dark/light titlebar colouring on Windows via DWM API."""
		try:
			style = ttk.Style()
			bg = style.lookup("TFrame", "background") or ""
			use_dark = 1 if self._is_dark_colour(bg) else 0

			if platform.system() == "Windows" and ctypes is not None and self.winfo_exists():
				hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
				if hwnd:
					DWMWA_USE_IMMERSIVE_DARK_MODE = 20
					ctypes.windll.dwmapi.DwmSetWindowAttribute(
						hwnd,
						DWMWA_USE_IMMERSIVE_DARK_MODE,
						ctypes.byref(ctypes.c_int(use_dark)),
						ctypes.sizeof(ctypes.c_int),
					)
		except Exception:
			pass

	@staticmethod
	def _is_dark_colour(colour: str) -> bool:
		"""Return True when the colour's perceived luminance is below the midpoint."""
		colour = (colour or "").strip().lstrip("#")
		if len(colour) == 3:
			colour = "".join(ch * 2 for ch in colour)
		if len(colour) != 6:
			return False
		try:
			r, g, b = int(colour[0:2], 16), int(colour[2:4], 16), int(colour[4:6], 16)
			return (0.299 * r + 0.587 * g + 0.114 * b) < 128
		except ValueError:
			return False
