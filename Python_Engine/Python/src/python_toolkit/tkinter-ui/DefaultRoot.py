import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable, Literal

try:
    import darkdetect
except ImportError:
    darkdetect = None
import ctypes


class DefaultRoot:
    """
    A reusable default root window template for tkinter applications.
    Includes a branded banner, content area, and optional action buttons.
    """

    def __init__(
        self,
        title: str = "Application",
        logo_path: Optional[Path] = None,
        min_width: int = 500,
        min_height: int = 400,
        width: Optional[int] = None,
        height: Optional[int] = None,
        resizable: bool = True,
        center_on_screen: bool = True,
        show_submit: bool = True,
        submit_text: str = "Submit",
        submit_command: Optional[Callable] = None,
        show_close: bool = True,
        close_text: str = "Close",
        close_command: Optional[Callable] = None,
        on_close_window: Optional[Callable] = None,
        theme_path: Optional[Path] = None,
        theme_mode: Literal["light", "dark", "auto"] = "auto",
    ):
        """
        Initialize the default root window.

        Args:
            title (str): Window and banner title text.
            logo_path (Path, optional): Path to logo image file.
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
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.minsize(min_width, min_height)
        self.root.resizable(resizable, resizable)
        
        # Hide window during setup to prevent flash
        self.root.withdraw()

        # Determine theme based on mode and system preference
        theme_name = self._determine_theme_name(theme_mode)
        self.theme_name = theme_name

        # Load custom dark theme
        self._load_theme(theme_path, theme_name)

        self.min_width = min_width
        self.min_height = min_height
        self.fixed_width = width
        self.fixed_height = height
        self.center_on_screen = center_on_screen
        self.submit_command = submit_command
        self.close_command = close_command
        self.result = None

        # Handle window close (X button)
        self.root.protocol("WM_DELETE_WINDOW", lambda: self._on_close_window(on_close_window))

        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Banner section
        self._build_banner(main_container, title, logo_path)

        # Content area (public access for adding widgets)
        self.content_frame = ttk.Frame(main_container, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Bottom button frame (if needed)
        if show_submit or show_close:
            self._build_buttons(main_container, show_submit, submit_text, show_close, close_text)

        # Apply sizing
        self._apply_sizing()

    def _determine_theme_name(self, theme_mode: str) -> str:
        """
        Determine the theme name based on the specified mode and system preference.
        
        Args:
            theme_mode (str): "light", "dark", or "auto"
            
        Returns:
            str: Theme name ("bhom_light" or "bhom_dark")
        """
        if theme_mode == "auto":
            # Try to detect system theme
            if darkdetect is not None:
                try:
                    is_dark = darkdetect.is_dark()
                    return "bhom_dark" if is_dark else "bhom_light"
                except Exception:
                    # Fall back to dark if detection fails
                    return "bhom_dark"
            else:
                # Default to dark if darkdetect not available
                return "bhom_dark"
        elif theme_mode == "light":
            return "bhom_light"
        else:  # "dark"
            return "bhom_dark"

    def _set_titlebar_theme(self, theme_name: str) -> None:
        """
        Apply titlebar theme using Windows API.
        
        Args:
            theme_name (str): Theme name ("bhom_light" or "bhom_dark")
        """
        try:
            import platform
            if platform.system() == "Windows" and ctypes is not None and self.root.winfo_exists():
                hwnd = self.root.winfo_id()
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd:
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    use_dark = 1 if theme_name == "bhom_dark" else 0
                    print(f"Applying titlebar theme: {theme_name} (dark={use_dark})")
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                        ctypes.byref(ctypes.c_int(use_dark)),
                        ctypes.sizeof(ctypes.c_int)
                    )
        except Exception:
            pass

    def _apply_titlebar_theme(self, theme_name: str) -> None:
        """
        Apply Windows titlebar theme using DWM API (deferred version).
        
        Args:
            theme_name (str): Theme name ("bhom_light" or "bhom_dark")
        """
        self._set_titlebar_theme(theme_name)

    def _load_theme(self, custom_theme_path: Optional[Path] = None, theme_name: str = "bhom_dark") -> None:
        """
        Load a custom theme from a TCL file.
        
        Args:
            custom_theme_path (Path, optional): Path to custom TCL theme file. 
                                                If None, uses default style.tcl in same directory.
            theme_name (str): Name of the theme to apply from the TCL file.
        """
        try:
            # Determine which theme file to use
            if custom_theme_path and custom_theme_path.exists():
                theme_path = custom_theme_path
            else:
                # Use default theme in same directory as this file
                current_dir = Path(__file__).parent
                theme_path = current_dir / "style.tcl"
            
            if theme_path.exists():
                # Load the TCL theme file
                self.root.tk.call('source', str(theme_path))
                
                # Apply the specified theme
                style = ttk.Style()
                style.theme_use(theme_name)
            else:
                print(f"Warning: Theme file not found at {theme_path}")
        except Exception as e:
            print(f"Warning: Could not load custom theme: {e}")

    def _build_banner(self, parent: ttk.Frame, title: str, logo_path: Optional[Path]) -> None:
        """Build the branded banner section."""
        banner = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=1)
        banner.pack(fill=tk.X, padx=0, pady=0)

        banner_content = ttk.Frame(banner, padding=10)
        banner_content.pack(fill=tk.X)

        # Logo (if provided)
        if logo_path and logo_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img.thumbnail((40, 40), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                logo_label = ttk.Label(banner_content, image=self.logo_image)
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            except ImportError:
                pass  # PIL not available, skip logo

        # Text container
        text_container = ttk.Frame(banner_content)
        text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            text_container,
            text=title,
            style="Title.TLabel"
        )
        title_label.pack(anchor="w")

        # Subtitle
        subtitle_label = ttk.Label(
            text_container,
            text="powered by BHoM",
            style="Caption.TLabel"
        )
        subtitle_label.pack(anchor="w")

    def _build_buttons(
        self,
        parent: ttk.Frame,
        show_submit: bool,
        submit_text: str,
        show_close: bool,
        close_text: str,
    ) -> None:
        """Build the bottom button bar."""
        button_bar = ttk.Frame(parent, padding=(20, 10))
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)

        button_container = ttk.Frame(button_bar)
        button_container.pack(anchor=tk.E)

        if show_close:
            self.close_button = ttk.Button(
                button_container, text=close_text, command=self._on_close
            )
            self.close_button.pack(side=tk.LEFT, padx=5)

        if show_submit:
            self.submit_button = ttk.Button(
                button_container, text=submit_text, command=self._on_submit
            )
            self.submit_button.pack(side=tk.LEFT, padx=5)

    def _apply_sizing(self) -> None:
        """Apply window sizing and positioning."""
        self.root.update_idletasks()

        # Determine final dimensions
        if self.fixed_width and self.fixed_height:
            final_width = self.fixed_width
            final_height = self.fixed_height
        elif self.fixed_width:
            final_width = self.fixed_width
            final_height = max(self.min_height, self.root.winfo_reqheight())
        elif self.fixed_height:
            final_width = max(self.min_width, self.root.winfo_reqwidth())
            final_height = self.fixed_height
        else:
            # Dynamic sizing
            final_width = max(self.min_width, self.root.winfo_reqwidth())
            final_height = max(self.min_height, self.root.winfo_reqheight())

        # Position
        if self.center_on_screen:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - final_width) // 2
            y = (screen_height - final_height) // 2
            self.root.geometry(f"{final_width}x{final_height}+{x}+{y}")
        else:
            self.root.geometry(f"{final_width}x{final_height}")
        
        # Defer window display until after styling is applied
        self.root.after(0, self._show_window_with_styling)

    def _show_window_with_styling(self) -> None:
        """Apply titlebar styling and show the window."""
        # Apply titlebar theme
        self._apply_titlebar_theme(self.theme_name)
        
        # Show window after styling
        self.root.deiconify()

    def refresh_sizing(self) -> None:
        """Recalculate and apply window sizing (useful after adding widgets)."""
        self._apply_sizing()

    def _on_submit(self) -> None:
        """Handle submit button click."""
        self.result = "submit"
        if self.submit_command:
            self.submit_command()
        self.root.destroy()

    def _on_close(self) -> None:
        """Handle close button click."""
        self.result = "close"
        if self.close_command:
            self.close_command()
        self.root.destroy()

    def _on_close_window(self, callback: Optional[Callable]) -> None:
        """Handle window X button click."""
        self.result = "window_closed"
        if callback:
            callback()
        self.root.destroy()

    def run(self) -> Optional[str]:
        """Show the window and return the result."""
        self.root.mainloop()
        return self.result


if __name__ == "__main__":
    from widgets.PathSelector import PathSelector
    from widgets.RadioSelection import RadioSelection
    from widgets.ValidatedEntryBox import ValidatedEntryBox
    from widgets.ListBox import ScrollableListBox

    # Store form state
    form_data = {}

    def on_submit():
        # Collect form data from widgets
        form_data["name"] = name_entry.get()
        form_data["age"] = age_entry.get_value()
        form_data["file_path"] = file_selector.get()
        form_data["priority"] = priority_radio.get()
        form_data["selected_items"] = listbox.get_selection()
        print("\nForm submitted with data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

    def on_close():
        print("Window closed without submitting")

    window = DefaultRoot(
        title="Example Form Application",
        min_width=600,
        min_height=500,
        submit_command=on_submit,
        close_command=on_close,
    )

    # Add form widgets to the content area
    ttk.Label(window.content_frame, text="Name:", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
    name_entry = ValidatedEntryBox(
        window.content_frame,
        value_type=str,
        min_length=2,
        max_length=50,
        required=True,
    )
    name_entry.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(window.content_frame, text="Age:", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
    age_entry = ValidatedEntryBox(
        window.content_frame,
        value_type=int,
        min_value=1,
        max_value=120,
        required=True,
    )
    age_entry.pack(fill=tk.X, pady=(0, 15))
    age_entry.set(25)

    ttk.Label(window.content_frame, text="Select a file:", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
    file_selector = PathSelector(
        window.content_frame,
        button_text="Browse...",
        filetypes=[("All Files", "*.*")],
        mode="file",
    )
    file_selector.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(window.content_frame, text="Priority:", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
    priority_radio = RadioSelection(
        window.content_frame,
        fields=["Low", "Medium", "High", "Critical"],
        default="Medium",
        orient="horizontal",
        max_per_line=4,
    )
    priority_radio.pack(anchor="w", pady=(0, 15))

    ttk.Label(window.content_frame, text="Select items:", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
    items = [f"Item {i}" for i in range(1, 11)]
    listbox = ScrollableListBox(
        window.content_frame,
        items=items,
        selectmode=tk.MULTIPLE,
        height=6,
        show_selection_controls=True,
    )
    listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    listbox.set_selections(["Item 2", "Item 5"])

    # Refresh window sizing after adding all widgets
    window.refresh_sizing()

    # Run the window
    result = window.run()
    print(f"\nWindow result: {result}")
    if result == "submit":
        print("Final form data:", form_data)
