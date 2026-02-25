"""Abstract base widget primitives used across BHoM Tkinter components."""

from abc import ABC, abstractmethod
from typing import cast

import tkinter as tk
from tkinter import ttk
from typing import Optional, Literal, Union, Tuple, Callable

from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

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
            custom_validation: Optional[Callable[[object], Tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]]] = None,
            disable_validation: bool = False,
            packing_options: PackingOptions = PackingOptions(),
            **kwargs):
        """
        Initialize the widget base.

        Args:
            parent: Parent widget
            id: Optional unique identifier for the widget
            item_title: Optional header text shown at the top of the widget frame.
            helper_text: Optional helper text shown above the entry box.
            alignment: Horizontal alignment for built-in text elements.
            custom_validation: Optional callable used to extend widget validation.
                Receives the current widget value and must return
                `(is_valid, message, severity)`.
            disable_validation: When `True`, all validation returns valid.
            **kwargs: Additional Frame options
        """
        super().__init__(parent, **kwargs)

        self.item_title = item_title
        self.helper_text = helper_text
        self.packing_options = packing_options
        self.alignment: Literal['left', 'center', 'right'] = self._normalise_alignment(alignment)
        self.custom_validation = custom_validation
        self.disable_validation = bool(disable_validation)

        if id is None:
            self.id = str(uuid4())
        else:
            self.id = id

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Subtitle.TLabel")
            self.title_label.pack(side="top", anchor=self._pack_anchor)
            self._apply_text_alignment(self.title_label)

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
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

        self._apply_text_alignment(widget)

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
            build_type: Literal['pack', 'grid', 'place'] = 'pack',
            **kwargs
        ):
        """Place the widget in its parent container.

        Args:
            build_type: Geometry manager strategy (`pack`, `grid`, or `place`).
            **kwargs: Additional geometry manager options.
        """
        if build_type == 'pack':
            self.pack(**self.packing_options.to_dict())

        elif build_type == 'grid':
            raise NotImplementedError("Grid packing is not yet implemented for BHoMBaseWidget.")
        
        elif build_type == 'place':
            raise NotImplementedError("Place packing is not yet implemented for BHoMBaseWidget.")
