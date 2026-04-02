from tkinter import ttk
import tkinter as tk
from typing import Optional, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget


class Label(BHoMBaseWidget):
    """Default BHoM label widget.

    This is a Frame-based widget (inherits `BHoMBaseWidget`) which contains
    an inner `ttk.Label` stored at `self.label`. Using a Frame wrapper allows
    built-in `item_title` and `helper_text` and consistent alignment handling
    across BHoM widgets.
    """

    def __init__(
            self,
            parent,
            text: str = "",
            item_title: Optional[str] = None,
            helper_text: Optional[str] = None,
            alignment: Optional[str] = None,
            image=None,
            style=None,
            justify=None,
            wraplength=None,
            anchor=None,
            width=None,
            compound=None,
            textvariable=None,
            foreground=None,
            font=None,
            **kwargs):
        def resolve(explicit_value, key: str, default=None):
            fallback = kwargs.pop(key, default)
            return explicit_value if explicit_value is not None else fallback

        base_options = {
            "item_title": resolve(item_title, "item_title"),
            "helper_text": resolve(helper_text, "helper_text"),
            "alignment": resolve(alignment, "alignment", "left") or "left",
        }

        label_options = {
            "text": resolve(text, "text", ""),
            "image": resolve(image, "image"),
            "style": resolve(style, "style"),
            "justify": resolve(justify, "justify"),
            "wraplength": resolve(wraplength, "wraplength"),
            "anchor": resolve(anchor, "anchor"),
            "width": resolve(width, "width"),
            "compound": resolve(compound, "compound"),
            "textvariable": resolve(textvariable, "textvariable"),
            "foreground": resolve(foreground, "foreground"),
            "font": resolve(font, "font"),
        }
        label_options = {key: value for key, value in label_options.items() if value is not None}

        # Initialize frame base without label-specific options to avoid passing
        # unknown options like '-image' to ttk.Frame
        super().__init__(
            parent,
            **base_options,
            **kwargs,
        )

        self.text = label_options.get("text", "")
        image_ref = label_options.get("image")
        if image_ref is not None:
            # Keep a Python-side reference so Tk image objects are not garbage-collected.
            self._image_ref = image_ref
        style_name = label_options.get("style")
        if "font" not in label_options and style_name:
            try:
                style_font = ttk.Style(self).lookup(style_name, "font")
                if style_font:
                    label_options["font"] = style_font
            except Exception:
                pass
        # Create inner ttk.Label with the collected options.
        # If a stale Tk image handle is passed from a previous failed run,
        # recover by dropping the image and creating a text-only label.
        try:
            self.label = ttk.Label(self.content_frame, **label_options)
        except tk.TclError as ex:
            message = str(ex).lower()
            if "image" in label_options and "image" in message and "doesn't exist" in message:
                safe_options = {k: v for k, v in label_options.items() if k != "image"}
                self.label = ttk.Label(self.content_frame, **safe_options)
            else:
                raise
        self.align_child_text(self.label)
        # Allow the inner label to expand horizontally so parent frames
        # using grid/pack with `fill='x'` will cause this label to fill
        # the available width (useful for option rows that should stretch).
        self.label.pack(side="top", anchor=self._pack_anchor, fill="x", expand=True)

    def get(self) -> str:
        """Return the current label text."""
        try:
            # Prefer text if present, otherwise return any image reference
            text = self.label.cget("text")
            if text:
                return str(text)
            # Fall back to any stored image reference
            return getattr(self, "_image_ref", "")
        except Exception:
            return ""

    def set(self, value):
        """Set the label text or image."""
        if isinstance(value, str):
            self.text = value
            self.label.configure(text=self.text, image="")
            if hasattr(self, "_image_ref"):
                delattr(self, "_image_ref")
        else:
            # Assume it's an image object
            self._image_ref = value
            self.label.configure(image=self._image_ref, text="")


    def update_text(self, new_text: str):
        """Backward-compatible method name used previously to update label text."""
        self.set(new_text)

    # Provide a generic `update` alias for convenience (matches previous API),
    # while remaining compatible with tkinter's parameterless `update()`.
    def update(self, new_text: Optional[str] = None):
        if new_text is None:
            super().update()
            return
        self.update_text(new_text)

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current content of the label.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for invalid content.
        """

        #always true
        return getattr(self, "apply_validation")((True, None, None))


if __name__ == "__main__":
    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

    root = BHoMBaseWindow()
    parent_frame = root.content_frame

    label_widget = Label(parent_frame, text="Hello, World!", build_options=PackingOptions(anchor="n", padx=10, pady=10), alignment="right")
    label_widget.build()

    label_widget2 = Label(parent_frame, text="Warning: This is a BHoM warning label.", build_options=PackingOptions(anchor="n", padx=10, pady=10), alignment="left", style="Warning.TLabel")
    label_widget2.build()

    root.mainloop()