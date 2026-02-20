import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Any, Union

class ValidatedEntryBox:
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
        parent: tk.Widget,
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
    ) -> None:
        """
        Initialize the ValidatedEntryBox.
        
        Args:
            parent: Parent widget
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
        self.parent = parent
        self.value_type = value_type
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.custom_validator = custom_validator
        self.on_validate = on_validate
        
        # Create frame to hold entry and error label
        self.frame = ttk.Frame(parent)
        
        # Create or use provided StringVar
        self.variable = variable if variable is not None else tk.StringVar(value="")
        
        # Create entry widget
        self.entry = ttk.Entry(self.frame, textvariable=self.variable, width=width)
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Bind validation events
        self.entry.bind("<FocusOut>", lambda _: self.validate())
        self.entry.bind("<Return>", lambda _: self.validate())
        
        # Create error label
        self.error_label = ttk.Label(self.frame, text="", style="Error.TLabel")
        self.error_label.pack(side="left", padx=(10, 0))
        
    def pack(self, **kwargs) -> None:
        """Pack the entry box frame."""
        self.frame.pack(**kwargs)
        
    def grid(self, **kwargs) -> None:
        """Grid the entry box frame."""
        self.frame.grid(**kwargs)
        
    def place(self, **kwargs) -> None:
        """Place the entry box frame."""
        self.frame.place(**kwargs)
        
    def get(self) -> str:
        """Get the current value as a string."""
        return self.variable.get().strip()
    
    def get_value(self) -> Optional[Union[str, int, float]]:
        """Get the current value converted to the specified type."""
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
        """Set the entry value."""
        self.variable.set(str(value))
        
    def validate(self) -> bool:
        """
        Validate the current entry value.
        
        Returns:
            bool: True if valid, False otherwise
        """
        value_str = self.get()
        
        # Check if required
        if self.required and not value_str:
            self._show_error("Required")
            self._call_validate_callback(False)
            return False
        
        # If not required and empty, it's valid
        if not self.required and not value_str:
            self._show_success()
            self._call_validate_callback(True)
            return True
        
        # Type-specific validation
        if self.value_type == str:
            return self._validate_string(value_str)
        elif self.value_type == int:
            return self._validate_int(value_str)
        elif self.value_type == float:
            return self._validate_float(value_str)
        else:
            self._show_error(f"Unsupported type: {self.value_type}")
            self._call_validate_callback(False)
            return False
    
    def _validate_string(self, value: str) -> bool:
        """Validate string value."""
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
        """Validate integer value."""
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
        """Validate float value."""
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
    
    def _show_success(self) -> None:
        """Display success indicator."""
        self.error_label.config(text="✓", foreground="#4bb543")
    
    def clear_error(self) -> None:
        """Clear the error message."""
        self.error_label.config(text="")
    
    def _call_validate_callback(self, is_valid: bool) -> None:
        """Call the validation callback if provided."""
        if self.on_validate:
            self.on_validate(is_valid)



if __name__ == "__main__":
    # Test the ValidatedEntryBox
    root = tk.Tk()
    root.title("Validated Entry Box Test")
    
    def on_validate(is_valid):
        print(f"Validation result: {is_valid}")
    
    entry_box = ValidatedEntryBox(root, value_type=int, min_value=0, max_value=100, on_validate=on_validate)
    entry_box.pack(padx=20, pady=20)
    
    root.mainloop()