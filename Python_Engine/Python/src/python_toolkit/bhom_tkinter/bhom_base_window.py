"""Base themed Tk window used by BHoM toolkit GUI windows."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from pathlib import Path
from typing import Optional, Callable, Literal, List
import platform
import ctypes
import os
import matplotlib as mpl

# Centralized matplotlib backend selection:
# - Allow override via `MPLBACKEND` environment variable (e.g. set to 'Agg' for headless CI).
# - Default to 'TkAgg' for Tkinter embedding; fallback to 'Agg' if the requested backend is unavailable.
backend = os.environ.get("MPLBACKEND")
if not backend:
    backend = "TkAgg"
try:
    mpl.use(backend, force=True)
except Exception:
    mpl.use("Agg", force=True)

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button
import python_toolkit
from python_toolkit.bhom_tkinter.theming.theme import ThemeManager
from python_toolkit.bhom_tkinter.bhom_window_shell import BHoMWindowShell

class BHoMBaseWindow(tk.Tk, BHoMWindowShell):
    """
    A reusable default root window template for tkinter applications.
    Includes a branded banner, content area, and optional action buttons.
    """

    def __init__(
        self,
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
        theme_mode:str = "auto",
        widgets: Optional[List[BHoMBaseWidget]] = None,
        top_most: bool = False,
        fullscreen: bool = False,
        buttons_side: Literal["left", "right"] = "right",
        grid_dimensions: Optional[tuple[int, int]] = None,
        show_banner: bool = True,
        defer_show: bool = False,
        content_padding: int = 20,
        **kwargs
    ):
        """
        Initialize the default root window.

        Args:
            title (str): Window and banner title text.
            logo_path (Path, optional): Path to logo image file.
            icon_path (Path, optional): Path to window icon file (.ico recommended on Windows).
            min_width (int): Minimum window width.
            min_height (int): Minimum window height.
            width (int, optional): Fixed width (overrides dynamic sizing).
            height (int, optional): Fixed height (overrides dynamic sizing).
            resizable (bool): Whether window can be resized.
            center_on_screen (bool): Center window on screen.
            show_submit (bool): Show submit button.
            submit_text (str): Text for submit button.
            submit_command (callable, optional): Command for submit button.
            show_close (bool): Show close button.
            close_text (str): Text for close button.
            close_command (callable, optional): Command for close button.
            on_close_window (callable, optional): Command when X is pressed.
            theme_path (Path, optional): Path to custom TCL theme file. If None, uses default style.tcl.
            theme_mode (str): Theme mode - "light", "dark", or "auto" to detect from system (default: "auto").
            fullscreen (bool): Whether the window starts in fullscreen mode (default: False).
            buttons_side (str): Side for buttons - "left" or "right" (default: "right").
            grid_dimensions (tuple[int, int], optional): If provided, configures content area with specified rows and columns for grid layout.
            show_banner (bool): Whether to render the branded banner header (default: True).
            defer_show (bool): If True, size the window but stay withdrawn until shown manually.
            content_padding (int): Padding applied to the content frame.
            **kwargs
        """
        super().__init__(**kwargs)
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


if __name__ == "__main__":


    ### TEST SIMPLE

    from python_toolkit.bhom_tkinter.widgets import Label, Button

    test = BHoMBaseWindow(
        title="Test Window",
        theme_mode="light",
    )

    test.widgets.append(Label(test.content_frame, text="Hello, World!"))
    test.widgets.append(Button(test.content_frame, text="Click Me", command=lambda: print("Button Clicked!"), helper_text="This is a button.", item_title="Button Widget Title"))

    test.build()
    test.mainloop()
    print(test.get())