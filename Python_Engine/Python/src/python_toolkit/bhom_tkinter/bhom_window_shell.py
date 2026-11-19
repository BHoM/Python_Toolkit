"""Shared themed window chrome mixin for BHoM root and child windows."""

import tkinter as tk
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
from pathlib import Path
from typing import Optional, Callable, Literal, List
import platform
import ctypes
import python_toolkit
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets._slim_scrollbar import SlimScrollbar, blend
from python_toolkit.bhom_tkinter.theming.theme import ThemeManager
from python_toolkit.bhom_tkinter.theming.scaling import init_scaling, scale, get_work_area

from python_toolkit.bhom import BHOM_VERSION


class BHoMWindowShell:
    """Shared themed window chrome for BHoM Tk root and Toplevel windows."""

    def _init_bhom_shell(
        self,
        *,
        title: str,
        min_width: int,
        min_height: int,
        width: Optional[int],
        height: Optional[int],
        resizable: bool,
        center_on_screen: bool,
        show_submit: bool,
        submit_text: str,
        submit_command: Optional[Callable],
        close_on_submit: bool,
        show_close: bool,
        close_text: str,
        close_command: Optional[Callable],
        on_close_window: Optional[Callable],
        theme_mode: str,
        widgets: Optional[List[BHoMBaseWidget]],
        top_most: bool,
        fullscreen: bool,
        buttons_side: Literal["left", "right"],
        grid_dimensions: Optional[tuple[int, int]],
        show_banner: bool = True,
        defer_show: bool = False,
        content_padding: int = 20,
    ) -> None:
        self.defer_show = defer_show
        # Must run before any widget/theme is created so pixel values use the right factor.
        init_scaling(self)
        min_width, min_height = scale(min_width), scale(min_height)
        width = scale(width) if width is not None else None
        height = scale(height) if height is not None else None
        content_padding = scale(content_padding)
        self.title(title)
        self._icon_image = None
        self.minsize(min_width, min_height)
        self.resizable(resizable, resizable)

        self.top_most = top_most
        self.attributes("-topmost", True)
        if not self.top_most:
            self.after(0, lambda: self.attributes("-topmost", False))

        self.fullscreen = fullscreen
        self.widgets = list(widgets) if widgets is not None else []
        self.withdraw()

        self.theme = ThemeManager(theme_mode)
        self._load_theme()
        self._set_window_icon()

        self.min_width = min_width
        self.min_height = min_height
        self.fixed_width = width
        self.fixed_height = height
        self.center_on_screen = center_on_screen
        self.submit_command = submit_command
        self.close_on_submit = close_on_submit
        self.close_command = close_command
        self.result = None
        self._is_exiting = False
        self.button_bar: Optional[ttk.Frame] = None
        self._has_been_shown = False
        self._pending_resize_job: Optional[str] = None
        self._is_resizing = False
        self._rigid_width = width is not None
        self._rigid_height = height is not None
        self._auto_fit_width = width is None
        self._auto_fit_height = height is None
        self._post_show_size_applied = False
        self.grid_dimensions = grid_dimensions
        self._cached_widget_values: dict[str, object] = {}

        self.protocol("WM_DELETE_WINDOW", lambda: self._on_close_window(on_close_window))

        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        if show_banner:
            self._build_banner(self.main_container, title, self.theme.logo_path)

        self._build_scroll_host(content_padding)

        if self.grid_dimensions:
            self.grid_content_frame(*self.grid_dimensions)

        if show_submit or show_close:
            self._build_buttons(
                self.main_container,
                show_submit,
                submit_text,
                show_close,
                close_text,
                buttons_side,
            )

        self._bind_dynamic_sizing()
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

        if any(not isinstance(w, BHoMBaseWidget) for w in self.widgets):
            raise TypeError("All items in widgets list must be instances of BHoMBaseWidget.")
        
        for widget in self.widgets:
            widget.build()

        self.refresh_sizing()

    def rebuild(self) -> None:
        """Re-place all widgets so changes to `self.widgets` are reflected.

        Every BHoM widget currently managed by the content frame is removed from
        its geometry manager (without being destroyed), then `build()` places the
        widgets that are still in `self.widgets`.
        """
        for child in self.content_frame.winfo_children():
            if not isinstance(child, BHoMBaseWidget):
                continue
            manager = child.winfo_manager()
            if manager == "pack":
                child.pack_forget()
            elif manager == "grid":
                child.grid_forget()
            elif manager == "place":
                child.place_forget()

        self.build()

    def _set_window_icon(self) -> None:
        """Set a custom window icon, replacing Tk's default icon."""
        icon_path = self.theme.icon_path

        if not icon_path:
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

    def _set_titlebar_theme(self) -> None:
        """
        Apply titlebar theme using Windows API.

        Args:
            theme_style: Theme style key (`light` or `dark`).

        Returns:
            None
        """
        try:
           
            use_dark = 1 if self.theme.dark_theme else 0

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

        except Exception:
            pass

    def _load_theme(self) -> str:
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
            
            expected_theme = self.theme.path.stem.replace("_theme", "")
            # Load the TCL theme file
            try:
                self.tk.call('source', str(self.theme.path))
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
            "TLabel": ("Segoe UI", 10),
            "Body.TLabel": ("Segoe UI", 10),
            "Caption.TLabel": ("Segoe UI", 9),
            "Small.TLabel": ("Segoe UI", 8),
            "Heading.TLabel": ("Segoe UI", 12, "bold"),
            "Subtitle.TLabel": ("Segoe UI", 12, "bold"),
            "Headline.TLabel": ("Segoe UI", 14, "bold"),
            "Title.TLabel": ("Segoe UI", 18, "bold"),
            "LargeTitle.TLabel": ("Segoe UI", 18, "bold"),
            "Display.TLabel": ("Segoe UI", 20, "bold"),
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
        self._banner = banner
        banner.pack(fill=tk.BOTH, padx=0, pady=0)

        banner_content = ttk.Frame(banner, padding=scale(10))
        banner_content.pack(fill=tk.BOTH, expand=True)

        # Text container
        text_container = ttk.Frame(banner_content)
        text_container.pack(side=tk.LEFT, fill=tk.Y)

        logo_container = ttk.Frame(banner_content, width=scale(80))
        logo_container.pack(side=tk.RIGHT, fill=tk.Y)

        # Logo (if provided)
        if logo_path and logo_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img.thumbnail((scale(80), scale(80)), Image.Resampling.LANCZOS)
                # Bind image to this root explicitly to avoid stale image handles
                # when previous runs failed and tore down a different Tk interpreter.
                self.logo_image = ImageTk.PhotoImage(img, master=self)
                logo_label = Label(logo_container, image=self.logo_image)
                logo_label.pack(fill=tk.BOTH, expand=True)
            except tk.TclError:
                pass
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
            text=f"powered by BHoM (v{BHOM_VERSION})",
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
        self.button_bar = ttk.Frame(parent, padding=(scale(20), scale(10)))
        self.button_bar.pack(side=tk.BOTTOM, fill=tk.X, before=self._scroll_host)

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
            submit_widget.pack(side=tk.LEFT, padx=scale(5))
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
            close_widget.pack(side=tk.LEFT, padx=scale(5))
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
        # Avoid fighting user-driven manual resize after the window is visible.
        # Initial sizing is handled by `_apply_sizing` + one post-show pass.
        if self._has_been_shown:
            return
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

    def _build_scroll_host(self, content_padding: int) -> None:
        """Create the content area inside a scroll host.

        The content normally sizes the window. If it cannot fit on screen (e.g. at
        high display scales) the host caps its height and shows a scrollbar, so the
        button bar below always stays reachable.
        """
        self._scroll_host = ttk.Frame(self.main_container)
        self._scroll_host.pack(fill=tk.BOTH, expand=True)

        background = ttk.Style().lookup("TFrame", "background") or self.cget("background")
        self._scroll_canvas = tk.Canvas(
            self._scroll_host, highlightthickness=0, borderwidth=0, background=background
        )
        background = ttk.Style().lookup("TFrame", "background") or "#1e1e1e"
        foreground = ttk.Style().lookup("TLabel", "foreground") or "#cccccc"
        try:
            colours = {
                "track": background,
                "thumb": blend(background, foreground, 0.30),
                "active": blend(background, foreground, 0.55),
            }
        except Exception:
            colours = {}
        bar_options = dict(thickness=scale(12), padding=scale(3), **colours)
        self._scroll_bar = SlimScrollbar(
            self._scroll_host, tk.VERTICAL, self._scroll_canvas.yview, **bar_options
        )
        self._scroll_hbar = SlimScrollbar(
            self._scroll_host, tk.HORIZONTAL, self._scroll_canvas.xview, **bar_options
        )
        self._scroll_canvas.configure(
            yscrollcommand=self._scroll_bar.set, xscrollcommand=self._scroll_hbar.set
        )
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scroll_bar_visible = False
        self._scroll_hbar_visible = False

        self.content_frame = ttk.Frame(self._scroll_canvas, padding=content_padding)
        self._content_window = self._scroll_canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw"
        )
        self._scroll_canvas.bind("<Configure>", self._on_scroll_canvas_configure)
        self.content_frame.bind("<Configure>", self._on_content_configure, add="+")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_content_configure(self, _event=None) -> None:
        self._update_scroll_region()

    def _update_scroll_region(self) -> None:
        """Scroll region always covers the content or the viewport, whichever is larger."""
        self._scroll_canvas.configure(
            scrollregion=(
                0,
                0,
                max(self._scroll_canvas.winfo_width(), self.content_frame.winfo_reqwidth()),
                max(self._scroll_canvas.winfo_height(), self.content_frame.winfo_reqheight()),
            )
        )

    def _on_scroll_canvas_configure(self, event=None) -> None:
        """Keep the content at least as large as the viewport and toggle the scrollbar."""
        width = self._scroll_canvas.winfo_width()
        height = self._scroll_canvas.winfo_height()
        req_height = self.content_frame.winfo_reqheight()
        self._scroll_canvas.itemconfigure(
            self._content_window,
            width=max(width, self.content_frame.winfo_reqwidth()),
            height=max(height, req_height),
        )
        self._update_scroll_region()
        self._scroll_host.update_idletasks()
        req_width = self.content_frame.winfo_reqwidth()
        # The bars take space from the viewport, so judge against the full host size.
        host_width = self._scroll_host.winfo_width()
        host_height = self._scroll_host.winfo_height()
        need_h = req_width > host_width + 1
        bar_h = self._scroll_hbar.winfo_reqheight() if need_h else 0
        need_v = req_height > host_height - bar_h + 1
        bar_w = self._scroll_bar.winfo_reqwidth() if need_v else 0
        need_h = req_width > host_width - bar_w + 1

        if need_h != self._scroll_hbar_visible:
            if need_h:
                self._scroll_hbar.pack(side=tk.BOTTOM, fill=tk.X, before=self._scroll_canvas)
            else:
                self._scroll_hbar.pack_forget()
                self._scroll_canvas.xview_moveto(0)
            self._scroll_hbar_visible = need_h
        if need_v != self._scroll_bar_visible:
            if need_v:
                self._scroll_bar.pack(side=tk.RIGHT, fill=tk.Y, before=self._scroll_canvas)
            else:
                self._scroll_bar.pack_forget()
                self._scroll_canvas.yview_moveto(0)
            self._scroll_bar_visible = need_v

    def _on_mousewheel(self, event) -> None:
        if not self._scroll_bar_visible:
            return
        # Let widgets with their own scrolling (list boxes, text, popdowns) handle it.
        if isinstance(event.widget, (tk.Listbox, tk.Text)) or "popdown" in str(event.widget):
            return
        try:
            if not str(event.widget).startswith(str(self)):
                return
        except Exception:
            return
        self._scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _update_scroll_host(self) -> None:
        """Request a viewport sized to the content, capped to the usable screen height."""
        self.update_idletasks()
        content_width = self.content_frame.winfo_reqwidth()
        content_height = self.content_frame.winfo_reqheight()

        work_width, work_height = get_work_area(self)
        chrome_height = scale(40)  # title bar + borders
        for part in (getattr(self, "button_bar", None),):
            if part is not None and part.winfo_manager():
                chrome_height += part.winfo_reqheight()
        banner = getattr(self, "_banner", None)
        if banner is not None:
            chrome_height += banner.winfo_reqheight()

        viewport_height = max(scale(120), min(content_height, work_height - chrome_height))
        viewport_width = min(content_width, work_width - scale(10))
        # Reserve room for scrollbars that will be needed.
        if content_width > viewport_width:
            viewport_height = max(scale(120), viewport_height - self._scroll_hbar.winfo_reqheight())
        if content_height > viewport_height:
            viewport_width = min(content_width + self._scroll_bar.winfo_reqwidth(), work_width - scale(10))
        self._scroll_canvas.configure(width=viewport_width, height=viewport_height)
        self._update_scroll_region()

    def _apply_sizing(self) -> None:
        """Apply window sizing and positioning."""
        self._pending_resize_job = None
        self._is_resizing = True
        self.update_idletasks()
        self._update_scroll_host()

        required_width = self.winfo_reqwidth()
        required_height = self.winfo_reqheight()

        if hasattr(self, "main_container"):
            required_width = max(required_width, self.main_container.winfo_reqwidth())
            required_height = max(required_height, self.main_container.winfo_reqheight())

        if self.button_bar is not None and self.button_bar.winfo_manager():
            required_height = max(required_height, self.button_bar.winfo_reqheight() + self._scroll_canvas.winfo_reqheight())

        # Determine final dimensions: auto-size unless a rigid dimension is explicitly provided.
        if self._rigid_width:
            final_width = max(self.min_width, int(self.fixed_width or 0))
        else:
            final_width = max(self.min_width, required_width)

        if self._rigid_height:
            final_height = max(self.min_height, int(self.fixed_height or 0))
        else:
            final_height = max(self.min_height, required_height)

        # Never exceed the usable screen area (scaled windows can outgrow small displays).
        final_width = min(final_width, self.winfo_screenwidth())
        final_height = min(final_height, self.winfo_screenheight() - scale(40))

        # Fullscreen overrides normal sizing/positioning
        if self.fullscreen:
            self.attributes("-fullscreen", True)
            if not getattr(self, "defer_show", False):
                self.after(0, self._show_window_with_styling)
            self._is_resizing = False
            return

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

        if getattr(self, "defer_show", False):
            self._is_resizing = False
            return

        # Defer window display until after styling is applied
        self.after(0, self._show_window_with_styling)
        self._is_resizing = False

    def _apply_post_show_sizing(self) -> None:
        """Run one extra grow-only size pass after first show.

        On some Windows setups, control metrics settle after deiconify/theme
        application, which can under-estimate initial required height and clip
        bottom controls.
        """
        if self._post_show_size_applied:
            return

        self.update_idletasks()

        required_width = self.winfo_reqwidth()
        required_height = self.winfo_reqheight()

        if hasattr(self, "main_container"):
            required_width = max(required_width, self.main_container.winfo_reqwidth())
            required_height = max(required_height, self.main_container.winfo_reqheight())

        if self.button_bar is not None and self.button_bar.winfo_manager():
            required_height = max(required_height, self.button_bar.winfo_reqheight() + self._scroll_canvas.winfo_reqheight())

        current_width = self.winfo_width()
        current_height = self.winfo_height()

        target_width = current_width
        target_height = current_height

        if self._auto_fit_width:
            target_width = max(current_width, self.min_width, required_width)
        elif self._rigid_width and self.fixed_width is not None:
            target_width = max(self.min_width, int(self.fixed_width))

        if self._auto_fit_height:
            target_height = max(current_height, self.min_height, required_height)
        elif self._rigid_height and self.fixed_height is not None:
            target_height = max(self.min_height, int(self.fixed_height))

        if target_width != current_width or target_height != current_height:
            x = self.winfo_x()
            y = self.winfo_y()
            self.geometry(f"{target_width}x{target_height}+{x}+{y}")

        self._post_show_size_applied = True

    def _show_window_with_styling(self) -> None:
        """Apply titlebar styling and show the window."""
        self._set_titlebar_theme()
        
        # Show window after styling
        self.deiconify()
        self._has_been_shown = True
        if not self._post_show_size_applied and (self._auto_fit_width or self._auto_fit_height):
            self.after_idle(self._apply_post_show_sizing)

    def refresh_sizing(self) -> None:
        """Recalculate and apply window sizing (useful after adding widgets)."""
        self._apply_sizing()

    def close(self) -> None:
        """Close and destroy the window. Override in subclasses for custom close behaviour."""
        self.destroy_root()

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
            # Capture values while widgets still exist so `get()` remains usable
            # after root teardown.
            self._cached_widget_values = self._collect_widget_values()
            self.destroy_root()

    def _on_submit(self) -> None:
        """Handle submit button click."""
        if self.close_on_submit:
            self._exit("submit", self.submit_command)
            return
        
        self.result = "submit"
        try:
            if self.submit_command:
                self.submit_command()
        except tk.TclError as ex:
            message = str(ex).lower()
            if not ("image" in message and "doesn't exist" in message):
                print(f"Warning: Exit callback raised an exception: {ex}")
        except Exception as ex:
            print(f"Warning: Exit callback raised an exception: {ex}")
        finally:
            self._cached_widget_values = self._collect_widget_values()


    def _on_close(self) -> None:
        """Handle close button click."""
        self._exit("close", self.close_command)

    def _on_close_window(self, callback: Optional[Callable]) -> None:
        """Handle window X button click."""
        self._exit("window_closed", callback)

    def get(self):
        try:
            if not self.winfo_exists():
                return dict(self._cached_widget_values)
        except Exception:
            return dict(self._cached_widget_values)

        widget_values = self._collect_widget_values()
        self._cached_widget_values = dict(widget_values)
        return widget_values

    def _collect_widget_values(self) -> dict[str, object]:
        """Collect values from all registered widgets."""
        widget_values: dict[str, object] = {}

        for widget in self.widgets:
            
            if hasattr(widget, "get"):
                try:
                    widget_values[widget.id] = widget.get()
                except Exception as ex:
                    print(f"Warning: Failed to get value from widget {widget}: {ex}")
        return widget_values


