"""Slim, rounded scrollbar drawn on a canvas (themed, DPI-aware)."""

import tkinter as tk
from typing import Callable, Optional


def blend(base: str, other: str, amount: float) -> str:
    """Blend two '#rrggbb' colours; amount=0 gives `base`, 1 gives `other`."""
    b = [int(base[i:i + 2], 16) for i in (1, 3, 5)]
    o = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * amount) for x, y in zip(b, o))


class SlimScrollbar(tk.Canvas):
    """Minimal scrollbar with a rounded thumb that brightens on hover.

    Implements the Tk scrollbar protocol (`set` + a scroll `command`), so it can be
    wired to `yscrollcommand` / `xscrollcommand` of any scrollable widget.
    """

    def __init__(
        self,
        parent: tk.Misc,
        orient: str = tk.VERTICAL,
        command: Optional[Callable] = None,
        *,
        track: str = "#1e1e1e",
        thumb: str = "#5a5a5a",
        active: str = "#8a8a8a",
        thickness: int = 12,
        padding: int = 3,
    ) -> None:
        self._vertical = orient == tk.VERTICAL
        self._command = command
        self._track, self._thumb, self._active = track, thumb, active
        self._thickness = thickness
        self._padding = padding
        self._first, self._last = 0.0, 1.0
        self._hover = False
        self._drag_offset: Optional[float] = None

        size = {"width": thickness} if self._vertical else {"height": thickness}
        super().__init__(parent, highlightthickness=0, borderwidth=0, background=track, **size)

        self.bind("<Configure>", lambda _e: self._redraw())
        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)

    # -- Tk scrollbar protocol -------------------------------------------------
    def set(self, first, last) -> None:
        self._first, self._last = float(first), float(last)
        self._redraw()

    # -- geometry ----------------------------------------------------------------
    def _length(self) -> float:
        return float(self.winfo_height() if self._vertical else self.winfo_width())

    def _thumb_span(self) -> tuple[float, float]:
        usable = max(1.0, self._length() - 2 * self._padding)
        start = self._padding + self._first * usable
        end = self._padding + self._last * usable
        min_len = self._thickness * 2
        if end - start < min_len:
            end = min(self._padding + usable, start + min_len)
            start = end - min_len
        return start, end

    def _redraw(self) -> None:
        self.delete("thumb")
        if self._first <= 0.0 and self._last >= 1.0:
            return
        start, end = self._thumb_span()
        width = max(2, self._thickness - 2 * self._padding)
        half = width / 2
        centre = self._thickness / 2
        colour = self._active if (self._hover or self._drag_offset is not None) else self._thumb
        if self._vertical:
            coords = (centre, start + half, centre, max(start + half, end - half))
        else:
            coords = (start + half, centre, max(start + half, end - half), centre)
        self.create_line(*coords, width=width, fill=colour, capstyle=tk.ROUND, tags="thumb")

    # -- interaction -------------------------------------------------------------
    def _set_hover(self, hover: bool) -> None:
        self._hover = hover
        self._redraw()

    def _position(self, event) -> float:
        return float(event.y if self._vertical else event.x)

    def _on_press(self, event) -> None:
        if self._command is None:
            return
        start, end = self._thumb_span()
        pos = self._position(event)
        if start <= pos <= end:
            self._drag_offset = pos - start
            self._redraw()
        else:
            self._command("scroll", -1 if pos < start else 1, "pages")

    def _on_drag(self, event) -> None:
        if self._drag_offset is None or self._command is None:
            return
        usable = max(1.0, self._length() - 2 * self._padding)
        fraction = (self._position(event) - self._drag_offset - self._padding) / usable
        self._command("moveto", max(0.0, min(1.0, fraction)))

    def _on_release(self, _event) -> None:
        self._drag_offset = None
        self._redraw()
