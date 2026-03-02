"""Base themed Tk window used by BHoM toolkit GUI windows."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from pathlib import Path
from typing import Optional, Callable, Literal, List
import darkdetect 
import platform
import ctypes
import os
import matplotlib as mpl

# Centralized matplotlib backend selection:
# - Allow override via `MPLBACKEND` environment variable (e.g. set to 'Agg' for headless CI).
# - Default to 'TkAgg' for Tkinter embedding; fallback to 'Agg' if the requested backend is unavailable.
backend = os.environ.get("MPLBACKEND")
if not backend:
    backend = "TkAgg"
try:
    mpl.use(backend, force=True)
except Exception:
    mpl.use("Agg", force=True)

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button
import python_toolkit

class BHoMBaseWindow(tk.Tk):
    """
    A reusable default root window template for tkinter applications.
    Includes a branded banner, content area, and optional action buttons.
    """

    def __init__(
        self,
        title: str = "Application",
        logo_path: Path = Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "BHoM_Logo.png",
        icon_path: Path = Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "bhom_icon.png",
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
        theme_path: Path = Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "bhom_light_theme.tcl",
        theme_path_dark: Path = Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "bhom_dark_theme.tcl",
        theme_mode: Literal["light", "dark", "auto"] = "auto",
        widgets: List[BHoMBaseWidget] = [],
        top_most: bool = True,
        buttons_side: Literal["left", "right"] = "right",
        grid_dimensions: Optional[tuple[int, int]] = None,
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
            buttons_side (str): Side for buttons - "left" or "right" (default: "right").
            grid_dimensions (tuple[int, int], optional): If provided, configures content area with specified rows and columns for grid layout.
            **kwargs
        """
        super().__init__(**kwargs)
        self.title(title)
        self._icon_image = None
        self.minsize(min_width, min_height)
        self.resizable(resizable, resizable)

        self.top_most = top_most
        if self.top_most:
            self.attributes("-topmost", True)

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
        self._is_exiting = False
        self.button_bar: Optional[ttk.Frame] = None
        self._has_been_shown = False
        self._pending_resize_job: Optional[str] = None
        self._is_resizing = False
        self._auto_fit_width = width is None
        self._auto_fit_height = height is None
        self.grid_dimensions = grid_dimensions

        # Handle window close (X button)
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_close_window(on_close_window))

        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Banner section
        self._build_banner(self.main_container, title, _logo_path)

        # Content area (public access for adding widgets)
        self.content_frame = ttk.Frame(self.main_container, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        if self.grid_dimensions:
            self.grid_content_frame(*self.grid_dimensions)

        # Bottom button frame (if needed)
        if show_submit or show_close:
            self._build_buttons(self.main_container, show_submit, submit_text, show_close, close_text, buttons_side)

        self._bind_dynamic_sizing()

        # Apply sizing
        self._apply_sizing()
        self.build()

    def grid_content_frame(self, x_count: int, y_count: int) -> None:
        """Configure the content frame with a grid layout of specified dimensions."""
        self.grid_dimensions = (x_count, y_count)
        for r in range(y_count):
            self.content_frame.rowconfigure(r, weight=1)
        for c in range(x_count):
            self.content_frame.columnconfigure(c, weight=1)
        
    def build(self):
        """Call build on all child widgets that have it (for deferred widget construction)."""
        for widget in self.widgets:
            if hasattr(widget, "build") and callable(getattr(widget, "build")):
                widget.build()

        
        self.refresh_sizing()

    def _set_window_icon(self, icon_path: Path) -> None:
        """Set a custom window icon, replacing Tk's default icon."""

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
        
        """Determine light or dark assets and theme based on configured mode.

        Args:
            logo_path: Light-mode logo path.
            dark_logo_path: Optional dark-mode logo path.
            icon_path: Light-mode icon path.
            dark_icon_path: Optional dark-mode icon path.
            theme_mode: Theme mode (`light`, `dark`, or `auto`).
            theme_path_light: Light theme Tcl path.
            theme_path_dark: Dark theme Tcl path.

        Returns:
            tuple[Path, Path, Path, str]: Theme path, logo path, icon path, and style key.
        """

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

        Args:
            theme_style: Theme style key (`light` or `dark`).

        Returns:
            str: Applied titlebar style key.
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
                expected_theme = theme_path.stem.replace("_theme", "")
                # Load the TCL theme file
                try:
                    self.tk.call('source', str(theme_path))
                except tk.TclError as source_error:
                    if "already exists" not in str(source_error).lower():
                        raise

                available_theme_names = style.theme_names()
                newly_added = [name for name in available_theme_names if name not in current_themes]
                if expected_theme in available_theme_names:
                    selected_theme = expected_theme
                elif newly_added:
                    selected_theme = newly_added[-1]
                else:
                    selected_theme = style.theme_use() if available_theme_names else "default"

                style.theme_use(selected_theme)
                self._ensure_typography_styles(style)
                return selected_theme
            else:
                print(f"Warning: Theme file not found at {theme_path}")
                available_theme_names = style.theme_names()
                selected_theme = available_theme_names[0] if available_theme_names else "default"
                style.theme_use(selected_theme)
                self._ensure_typography_styles(style)
                return selected_theme
            
        except Exception as e:
            print(f"Warning: Could not load custom theme: {e}")
            try:
                active_theme = style.theme_use()
                self._ensure_typography_styles(style)
                return active_theme
            except Exception:
                return "default"

    def _ensure_typography_styles(self, style: ttk.Style) -> None:
        """Ensure key typography styles exist and remain visually distinct."""
        defaults = {
            "TLabel": ("Segoe UI", 10, "bold"),
            "Body.TLabel": ("Segoe UI", 10),
            "Caption.TLabel": ("Segoe UI", 9),
            "Small.TLabel": ("Segoe UI", 8),
            "Heading.TLabel": ("Segoe UI", 12, "bold"),
            "Subtitle.TLabel": ("Segoe UI", 14, "bold"),
            "Headline.TLabel": ("Segoe UI", 16, "bold"),
            "Title.TLabel": ("Segoe UI", 24, "bold"),
            "LargeTitle.TLabel": ("Segoe UI", 24, "bold"),
            "Display.TLabel": ("Segoe UI", 28, "bold"),
        }

        def _lookup_font(style_name: str) -> str:
            try:
                return str(style.lookup(style_name, "font") or "").strip()
            except Exception:
                return ""

        for style_name, font_spec in defaults.items():
            if not _lookup_font(style_name):
                try:
                    style.configure(style_name, font=font_spec)
                except Exception:
                    pass

        base_font = _lookup_font("TLabel")
        for style_name, font_spec in (
            ("Caption.TLabel", defaults["Caption.TLabel"]),
            ("Subtitle.TLabel", defaults["Subtitle.TLabel"]),
            ("Headline.TLabel", defaults["Headline.TLabel"]),
            ("LargeTitle.TLabel", defaults["LargeTitle.TLabel"]),
        ):
            resolved = _lookup_font(style_name)
            if not resolved or resolved == base_font:
                try:
                    style.configure(style_name, font=font_spec)
                except Exception:
                    pass

    def _build_banner(self, parent: ttk.Frame, title: str, logo_path: Optional[Path]) -> None:
        """Build the branded banner section.

        Args:
            parent: Parent frame to host the banner.
            title: Banner title text.
            logo_path: Optional logo image path.
        """
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
                logo_label = Label(logo_container, image=self.logo_image)
                logo_label.pack(fill=tk.BOTH, expand=True)
            except ImportError:
                pass  # PIL not available, skip logo

        # Title
        title_label = Label(
            text_container,
            text=title,
            style="LargeTitle.TLabel"
        )
        title_label.pack(anchor="w")

        # Subtitle
        subtitle_label = Label(
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
        buttons_side: Literal["left", "right"] = "right"
    ) -> None:
        """Build the bottom button bar.

        Args:
            parent: Parent frame for the button bar.
            show_submit: Whether to create submit button.
            submit_text: Submit button label.
            show_close: Whether to create close button.
            close_text: Close button label.
        """
        self.button_bar = ttk.Frame(parent, padding=(20, 10))
        self.button_bar.pack(side=tk.BOTTOM, fill=tk.X)

        button_container = ttk.Frame(self.button_bar)
        button_container.pack(anchor=tk.E if buttons_side == "right" else tk.W)

        if show_submit:
            submit_widget = Button(
                button_container,
                text=submit_text,
                command=self._on_submit,
                style="Primary.TButton",
                width=12,
                alignment="center",
            )
            submit_widget.pack(side=tk.LEFT, padx=5)
            # expose inner ttk.Button for compatibility
            self.submit_button = submit_widget.button

        if show_close:
            close_widget = Button(
                button_container, 
                text=close_text, 
                command=self._on_close, 
                width=12,
                alignment="center",
            )
            close_widget.pack(side=tk.LEFT, padx=5)
            # expose inner ttk.Button for compatibility
            self.close_button = close_widget.button

    def _bind_dynamic_sizing(self) -> None:
        """Bind layout changes to schedule auto sizing updates."""
        self.main_container.bind("<Configure>", self._schedule_dynamic_sizing)
        self.content_frame.bind("<Configure>", self._schedule_dynamic_sizing)
        if self.button_bar is not None:
            self.button_bar.bind("<Configure>", self._schedule_dynamic_sizing)

    def _schedule_dynamic_sizing(self, _event=None) -> None:
        """Debounce dynamic sizing updates triggered by layout changes."""
        if self._is_resizing:
            return
        if not (self._auto_fit_width or self._auto_fit_height):
            return
        if self._pending_resize_job is not None:
            try:
                self.after_cancel(self._pending_resize_job)
            except Exception:
                pass
        self._pending_resize_job = self.after(30, self._apply_sizing)

    def _apply_sizing(self) -> None:
        """Apply window sizing and positioning."""
        self._pending_resize_job = None
        self._is_resizing = True
        self.update_idletasks()

        required_width = self.winfo_reqwidth()
        required_height = self.winfo_reqheight()

        if hasattr(self, "main_container"):
            required_width = max(required_width, self.main_container.winfo_reqwidth())
            required_height = max(required_height, self.main_container.winfo_reqheight())

        if self.button_bar is not None and self.button_bar.winfo_manager():
            required_height = max(required_height, self.button_bar.winfo_reqheight() + self.content_frame.winfo_reqheight())

        # Determine final dimensions
        if self.fixed_width and self.fixed_height:
            final_width = max(self.min_width, self.fixed_width, required_width)
            final_height = max(self.min_height, self.fixed_height, required_height)
        elif self.fixed_width:
            final_width = max(self.min_width, self.fixed_width, required_width)
            final_height = max(self.min_height, required_height)
        elif self.fixed_height:
            final_width = max(self.min_width, required_width)
            final_height = max(self.min_height, self.fixed_height, required_height)
        else:
            # Dynamic sizing
            final_width = max(self.min_width, required_width)
            final_height = max(self.min_height, required_height)

        # Position
        if self.center_on_screen and not self._has_been_shown:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - final_width) // 2
            y = (screen_height - final_height) // 2
            self.geometry(f"{final_width}x{final_height}+{x}+{y}")
        elif self._has_been_shown:
            x = self.winfo_x()
            y = self.winfo_y()
            self.geometry(f"{final_width}x{final_height}+{x}+{y}")
        else:
            self.geometry(f"{final_width}x{final_height}")
        
        # Defer window display until after styling is applied
        self.after(0, self._show_window_with_styling)
        self._is_resizing = False

    def _show_window_with_styling(self) -> None:
        """Apply titlebar styling and show the window."""
        # Apply titlebar theme
        self._set_titlebar_theme(self.titlebar_theme)
        
        # Show window after styling
        self.deiconify()
        self._has_been_shown = True

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
        """Handle any exit path and always destroy the root window.

        Args:
            result: Result token to store before closing.
            callback: Optional callback invoked before destruction.
        """
        if self._is_exiting:
            return
        self._is_exiting = True
        self.result = result
        try:
            if callback:
                callback()
        except tk.TclError as ex:
            message = str(ex).lower()
            if not ("image" in message and "doesn't exist" in message):
                print(f"Warning: Exit callback raised an exception: {ex}")
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

    from python_toolkit.bhom_tkinter.widgets import Label, Button

    test = BHoMBaseWindow(
        title="Test Window",
        theme_mode="dark",
    )

    test.widgets.append(Label(test.content_frame, text="Hello, World!"))
    test.widgets.append(Button(test.content_frame, text="Click Me", command=lambda: print("Button Clicked!"), helper_text="This is a button.", item_title="Button Widget Title"))

    test.build()
    test.mainloop()
