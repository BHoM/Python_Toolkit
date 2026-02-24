import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable, Literal, List
import darkdetect 
import platform
import ctypes

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget

class BHoMBaseWindow(tk.Tk):
    """
    A reusable default root window template for tkinter applications.
    Includes a branded banner, content area, and optional action buttons.
    """

    def __init__(
        self,
        title: str = "Application",
        logo_path: Path = Path(r"C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\src\python_toolkit\bhom\assets\BHoM_Logo.png"),
        icon_path: Path = Path(r"C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\src\python_toolkit\bhom\assets\bhom_icon.png"),
        dark_logo_path: Optional[Path] = None,
        dark_icon_path: Optional[Path] = None,
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
        theme_path: Path = Path(r"C:\GitHub_Files\Python_Toolkit\Python_Engine\Python\src\python_toolkit\bhom\bhom_light_theme.tcl"),
        theme_path_dark: Path = Path(r"C:\GitHub_Files\Python_Toolkit\Python_Engine\Python\src\python_toolkit\bhom\bhom_dark_theme.tcl"),
        theme_mode: Literal["light", "dark", "auto"] = "auto",
        widgets: List[BHoMBaseWidget] = [],
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
            **kwargs
        """
        super().__init__(**kwargs)
        self.title(title)
        self._icon_image = None
        self.minsize(min_width, min_height)
        self.resizable(resizable, resizable)

        self.widgets = widgets
        
        # Hide window during setup to prevent flash
        self.withdraw()

        # Load custom themes
        _theme_path, _logo_path, _icon_path, _theme_style = self._determine_theme(logo_path, dark_logo_path, icon_path, dark_icon_path, theme_mode, theme_path, theme_path_dark)
        
        self._set_window_icon(_icon_path)
        self.theme = self._load_theme(_theme_path)
        self.titlebar_theme = self._set_titlebar_theme(_theme_style)

        self.min_width = min_width
        self.min_height = min_height
        self.fixed_width = width
        self.fixed_height = height
        self.center_on_screen = center_on_screen
        self.submit_command = submit_command
        self.close_command = close_command
        self.result = None

        # Handle window close (X button)
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_close_window(on_close_window))

        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Banner section
        self._build_banner(main_container, title, _logo_path)

        # Content area (public access for adding widgets)
        self.content_frame = ttk.Frame(main_container, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Bottom button frame (if needed)
        if show_submit or show_close:
            self._build_buttons(main_container, show_submit, submit_text, show_close, close_text)

        # Apply sizing
        self._apply_sizing()

    def _set_window_icon(self, icon_path: Path) -> None:
        """Set a custom window icon, replacing the default uk icon."""

        if not icon_path.exists():
            print(f"Warning: Icon file not found at {icon_path}")
            return

        # Windows prefers .ico for titlebar/taskbar icons.
        if icon_path.suffix.lower() == ".ico":
            try:
                self.iconbitmap(default=str(icon_path))
                return
            except tk.TclError:
                pass

        # Fallback for image formats supported by Tk PhotoImage (png/gif/etc.).
        try:
            self._icon_image = tk.PhotoImage(file=str(icon_path))
            self.iconphoto(True, self._icon_image)
            return
        except tk.TclError:
            pass

        except Exception as ex:
            print(f"Warning: Could not set window icon from {icon_path}: {ex}")

    def _determine_theme(
            self, 
            logo_path: Path, 
            dark_logo_path: Optional[Path], 
            icon_path: Path, 
            dark_icon_path: Optional[Path], 
            theme_mode: str, 
            theme_path_light: Path, 
            theme_path_dark: Path) -> tuple[Path, Path, Path, str]:
        
        """determin the light or dark mode usage"""

        if theme_mode == "light":
            return theme_path_light, logo_path, icon_path, "light"
        
        if dark_logo_path is None:
            dark_logo_path = logo_path
        if dark_icon_path is None:
            dark_icon_path = icon_path

        if theme_mode == "dark":
            return theme_path_dark, dark_logo_path, dark_icon_path, "dark"
        
        #case == auto - detect system theme preference
        if darkdetect.isDark():
            return theme_path_dark, dark_logo_path, dark_icon_path, "dark"
        else:
            return theme_path_light, logo_path, icon_path, "light"

    def _set_titlebar_theme(self, theme_style: str) -> str:
        """
        Apply titlebar theme using Windows API.
        """
        try:
           
            use_dark = 1 if theme_style == "dark" else 0

            if platform.system() == "Windows" and ctypes is not None and self.winfo_exists():
                hwnd = self.winfo_id()
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                if hwnd:
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                        ctypes.byref(ctypes.c_int(use_dark)),
                        ctypes.sizeof(ctypes.c_int)
                    )

            if use_dark:
                return "dark"
            else:
                return "light"

        except Exception:
            return "light"

    def _load_theme(self, _theme_path: Path) -> str:
        """
        Load a custom theme from a TCL file.
        
        Args:
            custom_theme_path (Path, optional): Path to custom TCL theme file. 
                                                If None, uses default style.tcl in same directory.
            theme_name (str): Name of the theme to apply from the TCL file.

        Returns:
            str: Name of the theme that ended up being applied.
        """
        style = ttk.Style()

        try:
            current_themes = set(style.theme_names())

            # Determine which theme file to use
            if _theme_path and _theme_path.exists():
                theme_path = _theme_path
            else:
                # Use default theme
                theme_path = Path(r"C:\GitHub_Files\Python_Toolkit\Python_Engine\Python\src\python_toolkit\bhom\bhom_style.tcl")
            
            if theme_path.exists():
                # Load the TCL theme file
                self.tk.call('source', str(theme_path))

                available_theme_names = style.theme_names()
                newly_added = [name for name in available_theme_names if name not in current_themes]
                selected_theme = newly_added[-1] if newly_added else (available_theme_names[0] if available_theme_names else "default")

                style.theme_use(selected_theme)
                return selected_theme
            else:
                print(f"Warning: Theme file not found at {theme_path}")
                available_theme_names = style.theme_names()
                selected_theme = available_theme_names[0] if available_theme_names else "default"
                style.theme_use(selected_theme)
                return selected_theme
            
        except Exception as e:
            print(f"Warning: Could not load custom theme: {e}")
            try:
                return style.theme_use()
            except Exception:
                return "default"

    def _build_banner(self, parent: ttk.Frame, title: str, logo_path: Optional[Path]) -> None:
        """Build the branded banner section."""
        banner = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=1)
        banner.pack(fill=tk.BOTH, padx=0, pady=0)

        banner_content = ttk.Frame(banner, padding=10)
        banner_content.pack(fill=tk.BOTH, expand=True)

        # Text container
        text_container = ttk.Frame(banner_content)
        text_container.pack(side=tk.LEFT, fill=tk.Y)

        logo_container = ttk.Frame(banner_content, width=80)
        logo_container.pack(side=tk.RIGHT, fill=tk.Y)

        # Logo (if provided)
        if logo_path and logo_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img.thumbnail((80, 80), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                logo_label = ttk.Label(logo_container, image=self.logo_image)
                logo_label.pack(fill=tk.BOTH, expand=True)
            except ImportError:
                pass  # PIL not available, skip logo

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
        self.update_idletasks()

        # Determine final dimensions
        if self.fixed_width and self.fixed_height:
            final_width = self.fixed_width
            final_height = self.fixed_height
        elif self.fixed_width:
            final_width = self.fixed_width
            final_height = max(self.min_height, self.winfo_reqheight())
        elif self.fixed_height:
            final_width = max(self.min_width, self.winfo_reqwidth())
            final_height = self.fixed_height
        else:
            # Dynamic sizing
            final_width = max(self.min_width, self.winfo_reqwidth())
            final_height = max(self.min_height, self.winfo_reqheight())

        # Position
        if self.center_on_screen:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - final_width) // 2
            y = (screen_height - final_height) // 2
            self.geometry(f"{final_width}x{final_height}+{x}+{y}")
        else:
            self.geometry(f"{final_width}x{final_height}")
        
        # Defer window display until after styling is applied
        self.after(0, self._show_window_with_styling)

    def _show_window_with_styling(self) -> None:
        """Apply titlebar styling and show the window."""
        # Apply titlebar theme
        self._set_titlebar_theme(self.titlebar_theme)
        
        # Show window after styling
        self.deiconify()

    def refresh_sizing(self) -> None:
        """Recalculate and apply window sizing (useful after adding widgets)."""
        self._apply_sizing()

    def destroy_root(self) -> None:
        """Safely terminate and destroy the Tk root window."""

        try:
            if self.winfo_exists():
                self.quit()
                self.destroy()
        except tk.TclError:
            pass

    def _exit(self, result: str, callback: Optional[Callable] = None) -> None:
        """Handle any exit path and always destroy the root window."""
        self.result = result
        try:
            if callback:
                callback()
        except Exception as ex:
            print(f"Warning: Exit callback raised an exception: {ex}")
        finally:
            self.destroy_root()

    def _on_submit(self) -> None:
        """Handle submit button click."""
        self._exit("submit", self.submit_command)

    def _on_close(self) -> None:
        """Handle close button click."""
        self._exit("close", self.close_command)

    def _on_close_window(self, callback: Optional[Callable]) -> None:
        """Handle window X button click."""
        self._exit("window_closed", callback)


if __name__ == "__main__":


    ### TEST SIMPLE

    test = BHoMBaseWindow(
        title="Test Window",
        theme_mode="light",
    )

    test.mainloop()
    
    r""" 
    from widgets.PathSelector import PathSelector
    from widgets.RadioSelection import RadioSelection
    from widgets.ValidatedEntryBox import ValidatedEntryBox
    from widgets.ListBox import ScrollableListBox
    from widgets.CmapSelector import CmapSelector

    # Store form state
    form_data = {}

    def on_submit():
        # Collect form data from widgets
        form_data["name"] = name_entry.get()
        form_data["age"] = age_entry.get_value()
        form_data["file_path"] = file_selector.get()
        form_data["priority"] = priority_radio.get()
        form_data["selected_items"] = listbox.get_selection()
        form_data["cmap"] = cmap_selector.colormap_var.get()
        print("\nForm submitted with data:")
        for key, value in form_data.items():
            print(f"  {key}: {value}")

    def on_close():
        print("Window closed without submitting")

    window = BHoMBaseWindow(
        title="Example Form Application",
        min_width=600,
        min_height=500,
        submit_command=on_submit,
        close_command=on_close,
        logo_path= Path(r"C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\src\python_toolkit\bhom\assets\bhom_logo.png"),
        icon_path= Path(r"C:\ProgramData\BHoM\Extensions\PythonCode\Python_Toolkit\src\python_toolkit\bhom\assets\bhom_icon.png"),
        theme_mode="dark",

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

    cmap_selector = CmapSelector(window.content_frame, cmap_set="categorical")
    cmap_selector.pack(anchor="w", pady=(0, 10))

    # Refresh window sizing after adding all widgets
    window.refresh_sizing()

    # Run the window
    result = window.run()
    print(f"\nWindow result: {result}")
    if result == "submit":
        print("Final form data:", form_data)


    """
