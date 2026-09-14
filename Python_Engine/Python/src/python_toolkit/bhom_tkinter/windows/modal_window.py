"""Themed modal dialog window for child forms on a BHoM parent window."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow


class BHoMModalWindow(BHoMBaseChildWindow):
    """Modal child window with BHoM theming and a content area."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        title: str,
        width: int | None = None,
        height: int | None = None,
        min_width: int = 320,
        min_height: int = 240,
        resizable: bool = False,
        show_close: bool = True,
        close_text: str = "Close",
        close_command: Optional[Callable[[], None]] = None,
        theme_mode: str | None = None,
        content_padding: int = 20,
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            title=title,
            width=width,
            height=height,
            min_width=min_width,
            min_height=min_height,
            resizable=resizable,
            show_submit=False,
            show_close=show_close,
            close_text=close_text,
            close_command=close_command,
            theme_mode=theme_mode,
            content_padding=content_padding,
            show_banner=False,
            defer_show=True,
            modal=True,
            center_on_screen=False,
            **kwargs,
        )
