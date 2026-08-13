"""Themed Toplevel base class for BHoM child windows and dialogs."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Literal, List, Optional

from python_toolkit.bhom_tkinter.bhom_window_shell import BHoMWindowShell
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget


class BHoMBaseChildWindow(tk.Toplevel, BHoMWindowShell):
    """Themed child window for modals and standalone dialogs."""

    def __init__(
        self,
        parent: tk.Misc | None = None,
        *,
        title: str = "Application",
        min_width: int = 400,
        min_height: int = 400,
        width: Optional[int] = None,
        height: Optional[int] = None,
        resizable: bool = True,
        center_on_screen: bool = True,
        show_submit: bool = True,
        submit_text: str = "Submit",
        submit_command: Optional[Callable] = None,
        close_on_submit: bool = True,
        show_close: bool = True,
        close_text: str = "Close",
        close_command: Optional[Callable] = None,
        on_close_window: Optional[Callable] = None,
        theme_mode: str | None = None,
        widgets: Optional[List[BHoMBaseWidget]] = None,
        top_most: bool = False,
        fullscreen: bool = False,
        buttons_side: Literal["left", "right"] = "right",
        grid_dimensions: Optional[tuple[int, int]] = None,
        show_banner: bool = False,
        defer_show: bool = False,
        content_padding: int = 20,
        modal: bool = False,
        **kwargs,
    ) -> None:
        self._standalone_root: tk.Tk | None = None
        self._modal = modal
        self._modal_closed = False

        if parent is None:
            self._standalone_root = tk.Tk()
            self._standalone_root.withdraw()
            parent = self._standalone_root
        elif theme_mode is None and hasattr(parent, "theme"):
            theme_mode = "dark" if getattr(parent.theme, "dark_theme", False) else "light"

        if theme_mode is None:
            theme_mode = "auto"

        super().__init__(parent, **kwargs)
        if parent is not self._standalone_root:
            self.transient(parent)

        self._init_bhom_shell(
            title=title,
            min_width=min_width,
            min_height=min_height,
            width=width,
            height=height,
            resizable=resizable,
            center_on_screen=center_on_screen,
            show_submit=show_submit,
            submit_text=submit_text,
            submit_command=submit_command,
            close_on_submit=close_on_submit,
            show_close=show_close,
            close_text=close_text,
            close_command=close_command,
            on_close_window=on_close_window,
            theme_mode=theme_mode,
            widgets=widgets,
            top_most=top_most,
            fullscreen=fullscreen,
            buttons_side=buttons_side,
            grid_dimensions=grid_dimensions,
            show_banner=show_banner,
            defer_show=defer_show,
            content_padding=content_padding,
        )

        if modal:
            self.protocol("WM_DELETE_WINDOW", self.close)

        host = parent if parent is not self._standalone_root else None
        if host is not None and hasattr(host, "theme"):
            self.theme = host.theme
            self._load_theme()
            self._set_window_icon()

    def mainloop(self, n: int = 0) -> None:
        """Run the event loop for standalone dialogs, or block until closed."""
        if self._standalone_root is not None:
            self._standalone_root.mainloop(n)
            return
        self.wait_window()

    def show(self) -> None:
        """Display the child window and optionally capture input."""
        self._show_window_with_styling()
        if self._modal:
            self.grab_set()
            try:
                self.focus_force()
            except Exception:
                pass

    def run(self) -> None:
        """Show a modal child window and block until it closes."""
        self.show()
        self.wait_window()

    def close(self) -> None:
        """Close a modal child window and release the input grab."""
        if self._modal_closed:
            return
        self._modal_closed = True
        self._on_close()

    def destroy_root(self) -> None:
        """Destroy the child window without stopping a host application loop."""
        try:
            self.grab_release()
        except Exception:
            pass
        try:
            if self.winfo_exists():
                self.destroy()
        except tk.TclError:
            pass
        if self._standalone_root is not None:
            try:
                self._standalone_root.quit()
            except Exception:
                pass
            try:
                self._standalone_root.destroy()
            except tk.TclError:
                pass
