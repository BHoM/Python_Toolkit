"""Validated entry widget supporting typed value and constraint checks."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from typing import Optional, Callable, Any, Union, Literal

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

class ValidatedEntryBox(BHoMBaseWidget):
    """
    A reusable entry box component with built-in validation for different data types.
    
    Supports validation for:
    - String (required/optional, min/max length)
    - Integer (min/max value)
    - Float (min/max value)
    - Custom validation via callback
    """
    
    def __init__(
        self,
        parent,
        variable: Optional[tk.StringVar] = None,
        width: int = 15,
        value_type: type = str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True,
        custom_validator: Optional[Callable[[Any], tuple[bool, str]]] = None,
        on_validate: Optional[Callable[[bool], None]] = None,
        **kwargs
    ) -> None:
        """
        Initialize the ValidatedEntryBox.
        
        Args:
            parent: Parent
            item_title: Optional header text shown at the top of the widget frame
            requirements_text: Optional helper text shown above the entry box
            variable: StringVar to bind to the entry (creates one if not provided)
            width: Width of the entry widget
            value_type: Type to validate against (str, int, float)
            min_value: Minimum value for numeric types
            max_value: Maximum value for numeric types
            min_length: Minimum length for string type
            max_length: Maximum length for string type
            required: Whether the field is required
            custom_validator: Custom validation function that returns (is_valid, error_message)
            on_validate: Callback function called after validation with validation result
        """
        super().__init__(parent, **kwargs)
        self.value_type = value_type
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.custom_validator = custom_validator
        self.on_validate = on_validate

        # Create or use provided StringVar
        self.variable = variable if variable is not None else tk.StringVar(value="")
        
        # Create frame for entry and success indicator
        self.entry_frame = ttk.Frame(self.content_frame)
        self.entry_frame.pack(side="top", fill="x")
        
        # Create entry widget
        self.entry = ttk.Entry(self.entry_frame, textvariable=self.variable, width=width)
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Create success indicator label at end of entry
        self.success_label = Label(self.entry_frame, text=" ", foreground="#4bb543", width=2)
        getattr(self, "align_child_text")(self.success_label)
        self.success_label.pack(side="left", padx=(5, 0))
        
        # Create error label below entry with fixed height to prevent layout shifts
        self.error_label = Label(self.content_frame, text=" ", style="Caption.TLabel")
        getattr(self, "align_child_text")(self.error_label)
        self.error_label.pack(side="top", fill="x", anchor=getattr(self, "_pack_anchor"))
        
        # Bind validation events
        self.entry.bind("<FocusOut>", lambda _: self.validate())
        self.entry.bind("<Return>", lambda _: self.validate())
        
    def get(self) -> str:
        """Get the current value as a string.

        Returns:
            str: Trimmed entry value.
        """
        return self.variable.get().strip()
    
    def get_value(self) -> Optional[Union[str, int, float]]:
        """Get the current value converted to the specified type.

        Returns:
            Optional[Union[str, int, float]]: Parsed value, or `None` when empty/invalid.
        """
        value_str = self.get()
        if not value_str:
            return None
            
        try:
            if self.value_type == int:
                return int(value_str)
            elif self.value_type == float:
                return float(value_str)
            else:
                return value_str
        except (ValueError, TypeError):
            return None
    
    def set(self, value: Union[str, int, float]) -> None:
        """Set the entry value.

        Args:
            value: Value to display in the entry.
        """
        self.variable.set(str(value))
        
    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """
        Validate the current entry value.
        
        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for invalid input.
        """
        if self.disable_validation:
            self._show_success()
            self._call_validate_callback(True)
            return self.apply_validation((True, None, None))

        value_str = self.get()
        base_result: tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]
        
        # Check if required
        if self.required and not value_str:
            self._show_error("Required")
            self._call_validate_callback(False)
            base_result = (False, "Required", "error")
            return self.apply_validation(base_result)
        
        # If not required and empty, it's valid
        if not self.required and not value_str:
            self._show_success()
            self._call_validate_callback(True)
            base_result = (True, None, None)
            return self.apply_validation(base_result)
        
        # Type-specific validation
        if self.value_type == str:
            is_valid = self._validate_string(value_str)
        elif self.value_type == int:
            is_valid = self._validate_int(value_str)
        elif self.value_type == float:
            is_valid = self._validate_float(value_str)
        else:
            self._show_error(f"Unsupported type: {self.value_type}")
            self._call_validate_callback(False)
            base_result = (False, f"Unsupported type: {self.value_type}", "error")
            return self.apply_validation(base_result)

        if is_valid:
            base_result = (True, None, None)
        else:
            message = self.error_label.get().strip()
            base_result = (False, message if message else "Validation failed.", "error")

        final_result = self.apply_validation(base_result)
        final_valid, final_message, final_severity = final_result

        if final_valid:
            self._show_success()
            self._call_validate_callback(True)
        else:
            if final_message:
                self._show_error(final_message)
            else:
                self._show_error("Validation failed.")
            self._call_validate_callback(False)

        return final_result
    
    def _validate_string(self, value: str) -> bool:
        """Validate string value.

        Args:
            value: String value to validate.

        Returns:
            bool: `True` when valid, otherwise `False`.
        """
        # Check length constraints
        if self.min_length is not None and len(value) < self.min_length:
            self._show_error(f"Minimum length: {self.min_length}")
            self._call_validate_callback(False)
            return False
        
        if self.max_length is not None and len(value) > self.max_length:
            self._show_error(f"Maximum length: {self.max_length}")
            self._call_validate_callback(False)
            return False
        
        # Custom validation
        if self.custom_validator:
            is_valid, error_msg = self.custom_validator(value)
            if not is_valid:
                self._show_error(error_msg)
                self._call_validate_callback(False)
                return False
        
        self._show_success()
        self._call_validate_callback(True)
        return True
    
    def _validate_int(self, value_str: str) -> bool:
        """Validate integer value.

        Args:
            value_str: Raw entry text to parse as integer.

        Returns:
            bool: `True` when valid, otherwise `False`.
        """
        try:
            value = int(value_str)
        except ValueError:
            self._show_error("Must be a valid integer")
            self._call_validate_callback(False)
            return False
        
        # Check range constraints
        if self.min_value is not None and value < self.min_value:
            self._show_error(f"Must be >= {self.min_value}")
            self._call_validate_callback(False)
            return False
        
        if self.max_value is not None and value > self.max_value:
            self._show_error(f"Must be <= {self.max_value}")
            self._call_validate_callback(False)
            return False
        
        # Custom validation
        if self.custom_validator:
            is_valid, error_msg = self.custom_validator(value)
            if not is_valid:
                self._show_error(error_msg)
                self._call_validate_callback(False)
                return False
        
        self._show_success()
        self._call_validate_callback(True)
        return True
    
    def _validate_float(self, value_str: str) -> bool:
        """Validate float value.

        Args:
            value_str: Raw entry text to parse as float.

        Returns:
            bool: `True` when valid, otherwise `False`.
        """
        try:
            value = float(value_str)
        except ValueError:
            self._show_error("Must be a valid number")
            self._call_validate_callback(False)
            return False
        
        # Check range constraints
        if self.min_value is not None and value < self.min_value:
            if self.max_value is not None:
                self._show_error(f"Must be between {self.min_value} and {self.max_value}")
            else:
                self._show_error(f"Must be >= {self.min_value}")
            self._call_validate_callback(False)
            return False
        
        if self.max_value is not None and value > self.max_value:
            if self.min_value is not None:
                self._show_error(f"Must be between {self.min_value} and {self.max_value}")
            else:
                self._show_error(f"Must be <= {self.max_value}")
            self._call_validate_callback(False)
            return False
        
        # Custom validation
        if self.custom_validator:
            is_valid, error_msg = self.custom_validator(value)
            if not is_valid:
                self._show_error(error_msg)
                self._call_validate_callback(False)
                return False
        
        self._show_success()
        self._call_validate_callback(True)
        return True
    
    def _show_error(self, message: str) -> None:
        """Display error message."""
        self.error_label.config(text=message, foreground="#ff4444")
        self.success_label.config(text=" ")
    
    def _show_success(self) -> None:
        """Display success indicator."""
        self.error_label.config(text=" ")
        self.success_label.config(text="✓")
    
    def clear_error(self) -> None:
        """Clear the error message."""
        self.error_label.config(text=" ")
        self.success_label.config(text=" ")
    
    def _call_validate_callback(self, is_valid: bool) -> None:
        """Call the validation callback if provided."""
        if self.on_validate:
            self.on_validate(is_valid)



if __name__ == "__main__":
    # Test the ValidatedEntryBox

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
    
    root = BHoMBaseWindow(title="Validated Entry Box Test")
    parent_container = getattr(root, "content_frame", root)

    def on_validate(is_valid):
        """Print validation state in the standalone example."""
        print(f"Validation result: {is_valid}")
    
    entry_box = ValidatedEntryBox(
        parent_container,
        item_title="Integer Field",
        helper_text="Enter an integer from 0 to 100",
        value_type=int,
        min_value=0,
        max_value=100,
        on_validate=on_validate,
        packing_options=PackingOptions(padx=20, pady=20)
    )
    entry_box.build()
    
    root.mainloop()