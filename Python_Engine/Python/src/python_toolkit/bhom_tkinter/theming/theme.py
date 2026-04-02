from dataclasses import dataclass
from pathlib import Path
import python_toolkit

@dataclass
class TclTheme:
    name: str
    path: Path
    logo_path: Path|None = None
    icon_path: Path|None = None
    dark_theme: bool = False

    def __post_init__(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Theme file not found at {self.path}")
        if self.logo_path and not self.logo_path.exists():
            raise FileNotFoundError(f"Logo file not found at {self.logo_path}")
        if self.icon_path and not self.icon_path.exists():
            raise FileNotFoundError(f"Icon file not found at {self.icon_path}")

LIGHT = TclTheme(
    name="light", 
    path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom_tkinter" / "theming" / "bhom_light_theme.tcl",
    logo_path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "BHoM_Logo.png",
    icon_path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "bhom_icon.png",
    dark_theme=False
)

DARK = TclTheme(
    name="dark", 
    path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom_tkinter" / "theming" / "bhom_dark_theme.tcl",
    logo_path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "BHoM_Logo.png",
    icon_path=Path(list(python_toolkit.__path__)[0]).absolute() / "bhom" / "assets" / "bhom_icon.png",
    dark_theme=True
    )

class ThemeManager:
    def __init__(self, theme_mode: str = "light"):
        self.theme_mode = theme_mode
        self.themes = {
            "light": LIGHT,
            "dark": DARK,
            "auto": DARK if self._is_windows_dark_mode() else LIGHT,
            "default": LIGHT
        }

    def register_theme(self, theme: TclTheme) -> None:
        """Register a custom theme."""
        self.themes[theme.name] = theme

    def set_theme_mode(self, mode: str) -> None:
        """Set the current theme mode."""
        if mode not in self.themes:
            raise ValueError(f"Invalid theme mode: {mode}")
        self.theme_mode = mode

    def add_new_theme(self, name: str, path: Path, logo_path: Path|None = None, icon_path: Path|None = None, dark_theme: bool = False) -> None:
        """Add a new theme by providing its details."""
        new_theme = TclTheme(name=name, path=path, logo_path=logo_path, icon_path=icon_path, dark_theme=dark_theme)
        self.register_theme(new_theme)

    @property
    def name(self) -> str:
        return self.get_theme().name
    
    @name.setter
    def name(self, value: str) -> None:
        if value not in self.themes:
            raise ValueError(f"Invalid theme name: {value}")
        self.set_theme_mode(value)
    
    @property
    def path(self) -> Path:
        return self.get_theme().path
    
    @path.setter
    def path(self, value: Path) -> None:
        theme = self.get_theme()
        theme.path = value
    
    @property
    def logo_path(self) -> Path|None:
        return self.get_theme().logo_path
    
    @logo_path.setter
    def logo_path(self, value: Path|None) -> None:
        theme = self.get_theme()
        theme.logo_path = value
    
    @property
    def icon_path(self) -> Path|None:
        return self.get_theme().icon_path
    
    @icon_path.setter
    def icon_path(self, value: Path|None) -> None:
        theme = self.get_theme()
        theme.icon_path = value
    
    @property
    def dark_theme(self) -> bool:
        return self.get_theme().dark_theme
    
    @dark_theme.setter
    def dark_theme(self, value: bool) -> None:
        theme = self.get_theme()
        theme.dark_theme = value
    
    def get_theme(self, theme_mode: str | None = None) -> TclTheme:
        if theme_mode is None:
            theme_mode = self.theme_mode
        if theme_mode not in self.themes:
            raise ValueError(f"Invalid theme mode: {theme_mode}")
        return self.themes[theme_mode]
    
    def _is_windows_dark_mode(self) -> bool:
        
        try:
            
            import winreg
            key = winreg.OpenKey(
				winreg.HKEY_CURRENT_USER,
				r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
			)
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")

            return value == 0 # 0 means dark mode, 1 means light mode
        
        except FileNotFoundError:
			# Key may not exist on older Windows versions
            return False
        
        except ImportError:
            # winreg is only available on Windows
            return False