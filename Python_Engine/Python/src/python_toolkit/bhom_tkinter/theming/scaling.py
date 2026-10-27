"""DPI scaling helpers for BHoM Tkinter windows.

Tk scales font sizes (points) with the display DPI but leaves pixel values
untouched, so hard-coded paddings, minimum sizes and images look cramped at
display scales above 100%. All pixel values in the toolkit are authored for a
96 DPI (100%) display and are converted through `scale` / `scale_pad`.
"""

import ctypes
import platform
import tkinter as tk
from typing import Any

BASE_DPI = 96.0

_scale_factor: float = 1.0


def enable_dpi_awareness() -> None:
    """Opt the process in to DPI awareness on Windows (no-op elsewhere).

    Must run before the first Tk window is created. Safe to call repeatedly or
    when the host process (or matplotlib) has already set an awareness level.
    """
    if platform.system() != "Windows":
        return
    try:
        # Per-monitor v2 (Windows 10 1703+).
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def init_scaling(root: tk.Misc) -> float:
    """Detect the display scale from `root`, sync Tk's own scaling and cache the factor.

    Returns:
        float: Scale factor relative to 96 DPI (1.25 for a 125% display).
    """
    global _scale_factor
    try:
        dpi = float(root.winfo_fpixels("1i"))
    except Exception:
        dpi = BASE_DPI
    if dpi <= 0:
        dpi = BASE_DPI
    _scale_factor = max(1.0, dpi / BASE_DPI)

    # Keep points->pixels (fonts) consistent with the pixel scale.
    try:
        root.tk.call("tk", "scaling", dpi / 72.0)
    except Exception:
        pass
    # Expose the factor to the Tcl theme files (see `px` proc in the themes).
    try:
        root.tk.call("set", "::bhom_scale", _scale_factor)
    except Exception:
        pass
    return _scale_factor


def get_work_area(root: tk.Misc) -> tuple[int, int]:
    """Return the usable (width, height) of the primary screen, excluding the taskbar."""
    if platform.system() == "Windows":
        try:
            from ctypes import wintypes
            rect = wintypes.RECT()
            # SPI_GETWORKAREA = 0x0030
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                return rect.right - rect.left, rect.bottom - rect.top
        except Exception:
            pass
    return root.winfo_screenwidth(), root.winfo_screenheight()


def get_scale_factor() -> float:
    """Return the cached scale factor (1.0 until `init_scaling` has run)."""
    return _scale_factor


def scale(value: Any) -> Any:
    """Scale a 96 DPI pixel value. Non-numeric values (e.g. '5p') pass through."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if value == 0:
        return value
    scaled = int(round(value * _scale_factor))
    # Never let a non-zero distance collapse to zero.
    return scaled if scaled != 0 else (1 if value > 0 else -1)


def scale_pad(value: Any) -> Any:
    """Scale a pad value that may be a single value or a (before, after) tuple."""
    if isinstance(value, (tuple, list)):
        return tuple(scale(v) for v in value)
    return scale(value)
