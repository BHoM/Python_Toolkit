"""Abstract base widget primitives used across BHoM Tkinter components."""

from abc import ABC, abstractmethod
from typing import cast

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal, Union, Tuple, Callable

from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
from python_toolkit.bhom_tkinter.widgets._build_options import BuildOptions
from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions

from uuid import uuid4

class BHoMBaseWidget(ttk.Frame, ABC):
    """
    Base class for all widgets in the BHoM Tkinter toolkit.
    Provides common structure and functionality for consistent design.
    """

    def __init__(
            self, 
            parent: ttk.Frame, 
            id: Optional[str] = None, 
            item_title: Optional[str] = None, 
            helper_text: Optional[str] = None, 
            alignment: Literal['left', 'center', 'right'] = 'left',
            fill_extents: bool = False,
            custom_validation: Optional[Callable[[object], Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]]] = None,
            disable_validation: bool = False,
            build_options: BuildOptions = PackingOptions(),
            on_change: Optional[Callable] = None,
            **kwargs):
        """
        Initialize the widget base.

        Args:
            parent: Parent widget
            id: Optional unique identifier for the widget
            item_title: Optional header text shown at the top of the widget frame.
            helper_text: Optional helper text shown above the entry box.
            alignment: Horizontal alignment for built-in text elements.
            fill_extents: If `True`, built-in title/helper labels fill horizontal
                extent (`fill='x'`). If `False`, labels use natural width.
            custom_validation: Optional callable used to extend widget validation.
                Receives the current widget value and must return
                `(is_valid, message, severity)`.
            disable_validation: When `True`, all validation returns valid.
            on_change: Optional callback invoked whenever the widget value
                changes.  The current value is passed as the single argument.
                Supported by all widgets; supplements widget-specific ``command``
                parameters where those exist.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.item_title = item_title
        self.helper_text = helper_text
        self.build_options = build_options
        self.alignment: Literal['left', 'center', 'right'] = self._normalise_alignment(alignment)
        self.fill_extents = self._normalise_bool(fill_extents)
        self.custom_validation = custom_validation
        self.disable_validation = bool(disable_validation)
        self.on_change: Optional[Callable] = on_change

        if id is None:
            self.id = str(uuid4())
        else:
            self.id = id

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Subtitle.TLabel")
            try:
                title_font = ttk.Style(self).lookup("Subtitle.TLabel", "font")
                if title_font:
                    self.title_label.configure(font=title_font)
            except Exception:
                pass
            if self.fill_extents:
                self.title_label.pack(side="top", anchor=self._pack_anchor, fill=tk.X)
            else:
                self.title_label.pack(side="top", anchor=self._pack_anchor)
            self._apply_text_alignment(self.title_label)

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
            try:
                helper_font = ttk.Style(self).lookup("Caption.TLabel", "font")
                if helper_font:
                    self.helper_label.configure(font=helper_font)
            except Exception:
                pass
            if self.fill_extents:
                self.helper_label.pack(side="top", anchor=self._pack_anchor, fill=tk.X)
            else:
                self.helper_label.pack(side="top", anchor=self._pack_anchor)
            self._apply_text_alignment(self.helper_label)

        # Container frame for embedded content (not title/helper)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(side="top", fill=tk.BOTH, expand=True)

    @property
    def _pack_anchor(self) -> Literal['w', 'center', 'e']:
        """Return the pack anchor string for the current alignment.

        Returns:
            str: Pack anchor token (`w`, `center`, or `e`).
        """
        return cast(Literal['w', 'center', 'e'], {
            "left": "w",
            "center": "center",
            "right": "e",
        }[self.alignment])

    @property
    def _text_anchor(self) -> Literal['w', 'center', 'e']:
        """Return the text anchor string for the current alignment.

        Returns:
            str: Text anchor token (`w`, `center`, or `e`).
        """
        return cast(Literal['w', 'center', 'e'], {
            "left": "w",
            "center": "center",
            "right": "e",
        }[self.alignment])

    @property
    def _text_justify(self) -> Literal['left', 'center', 'right']:
        """Return the Tk justify token for the current alignment.

        Returns:
            str: Justification token (`left`, `center`, or `right`).
        """
        return cast(Literal['left', 'center', 'right'], self.alignment)

    @property
    def _grid_sticky(self) -> Literal['w', '', 'e']:
        """Return the grid sticky token for the current alignment.

        Returns:
            str: Grid sticky token (`w`, empty string for centered, or `e`).
        """
        return cast(Literal['w', '', 'e'], {
            "left": "w",
            "center": "",
            "right": "e",
        }[self.alignment])

    def _normalise_alignment(self, alignment: Optional[str]) -> Literal['left', 'center', 'right']:
        """Normalise alignment input and fallback safely to `left`.

        Args:
            alignment: Candidate alignment value.

        Returns:
            Literal['left', 'center', 'right']: Normalised alignment.
        """
        candidate = str(alignment or "left").strip().lower()
        if candidate not in {"left", "center", "right"}:
            return "left"
        return cast(Literal['left', 'center', 'right'], candidate)

    def _normalise_bool(self, value: object) -> bool:
        """Normalise bool-like input with safe defaults.

        Args:
            value: Candidate boolean input.

        Returns:
            bool: Parsed boolean value.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            candidate = value.strip().lower()
            if candidate in {"1", "true", "yes", "y", "on"}:
                return True
            if candidate in {"0", "false", "no", "n", "off", ""}:
                return False
        return bool(value)

    def _apply_text_alignment(self, widget: tk.Widget) -> None:
        """Apply current alignment settings to a text-capable Tk widget.

        Args:
            widget: Tk/ttk widget that may support `anchor` and/or `justify`.
        """
        try:
            configure_keys = set(widget.configure().keys())
        except Exception:
            return

        options = {}
        if "anchor" in configure_keys:
            options["anchor"] = self._text_anchor
        if "justify" in configure_keys:
            options["justify"] = self._text_justify

        if options:
            try:
                widget.configure(**options)
            except Exception:
                pass

    def align_child_text(self, widget: tk.Widget, alignment: Optional[Literal['left', 'center', 'right']] = None) -> None:
        """Apply left/center/right text alignment to a child widget.

        Args:
            widget: Child text widget to align.
            alignment: Optional override alignment for this call.
        """
        previous_alignment = self.alignment
        if alignment is not None:
            self.alignment = self._normalise_alignment(alignment)

        try:
            self._apply_text_alignment(widget)
        finally:
            if alignment is not None:
                self.alignment = previous_alignment

    def set_alignment(self, alignment: Literal['left', 'center', 'right']) -> None:
        """Set widget-wide alignment and refresh built-in labels.

        Args:
            alignment: Horizontal alignment (`left`, `center`, or `right`).
        """
        self.alignment = self._normalise_alignment(alignment)

        for label_name in ("title_label", "helper_label"):
            label = getattr(self, label_name, None)
            if label is not None:
                label.pack_configure(anchor=self._pack_anchor)
                self._apply_text_alignment(label)

    def set_fill_extents(self, fill_extents: bool) -> None:
        """Set whether built-in title/helper labels fill horizontal extent.

        Args:
            fill_extents: `True` for `fill='x'`, else natural-width packing.
        """
        self.fill_extents = self._normalise_bool(fill_extents)

        for label_name in ("title_label", "helper_label"):
            label = getattr(self, label_name, None)
            if label is None:
                continue
            label.pack_configure(fill=(tk.X if self.fill_extents else "none"))
            label.pack_configure(anchor=self._pack_anchor)
            self._apply_text_alignment(label)

    def _fire_on_change(self, value: object) -> None:
        """Invoke the ``on_change`` callback with the current widget value.

        This is called internally by each widget subclass whenever its value
        changes.  It is safe to call even when ``on_change`` is ``None``.

        Args:
            value: The current widget value to pass to the callback.
        """
        if self.on_change is not None:
            try:
                self.on_change(value)
            except Exception:
                pass

    @abstractmethod
    def get(self):
        """Get the current value of the widget."""
        raise NotImplementedError("Subclasses must implement the get() method.")

    @abstractmethod
    def set(self, value):
        """Set the value of the widget.

        Args:
            value: Value to apply to the widget state.
        """
        raise NotImplementedError("Subclasses must implement the set() method.")

    @abstractmethod
    def validate(self) -> Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the current widget value.

        Returns:
            bool: True if the current value is valid, False otherwise.
            Optional[str]: Error message if the value is invalid, None otherwise.
            Optional[Literal['info', 'warning', 'error']]: Severity level of the validation result, or None if valid.
        """
        raise NotImplementedError("Subclasses must implement the validate() method.")

    def apply_validation(
            self,
            base_result: Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]
        ) -> Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Apply global validation switches and optional custom validation.

        Subclasses should call this from their `validate()` implementation,
        passing built-in validation output as `base_result`.

        Args:
            base_result: Built-in widget validation result in the form
                `(is_valid, message, severity)`.

        Returns:
            Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                Final validation result after applying disable/custom rules.
        """
        if self.disable_validation:
            return True, None, None

        is_valid, message, severity = base_result
        if not is_valid:
            return is_valid, message, severity or "error"

        if self.custom_validation is None:
            return is_valid, message, severity

        try:
            custom_result = self.custom_validation(self.get())
        except Exception as ex:
            return False, f"Custom validation failed: {ex}", "error"

        if not isinstance(custom_result, tuple) or len(custom_result) != 3:
            return False, "Custom validation must return (is_valid, message, severity).", "error"

        custom_valid, custom_message, custom_severity = custom_result
        if not custom_valid:
            return False, custom_message, custom_severity or "error"

        if custom_message is not None or custom_severity is not None:
            return True, custom_message, custom_severity

        return is_valid, message, severity
    
    def build(
            self, 
            **kwargs
        ):
        """Place the widget in its parent container.

        Args:
            build_type: Geometry manager strategy (`pack`, `grid`, or `place`).
            **kwargs: Additional geometry manager options.
        """
        if isinstance(self.build_options, PackingOptions):
            self.pack(**self.build_options.to_dict())

        elif isinstance(self.build_options, GridOptions):
            self.grid(**self.build_options.to_dict())
        
        else:
            raise NotImplementedError(f"Unsupported build options type: {type(self.build_options)}")



if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
    from python_toolkit.bhom_tkinter.widgets._grid_options import GridOptions

    from python_toolkit.bhom_tkinter.widgets.button import Button 
    from python_toolkit.bhom_tkinter.widgets.label import Label    

    #gridding test

    root = BHoMBaseWindow(grid_dimensions=(3, 3))

    grid_options = GridOptions(sticky="n", padx=5, pady=5)

    for i in range(3):
        for j in range(3):
            sub = grid_options.__class__(**{**grid_options.to_dict(), "row": i, "column": j})
            label = Label(root.content_frame, text=f"Row {i} - Column {j}", build_options=sub)

            root.widgets.append(label)

    root.build()
    root.mainloop()
