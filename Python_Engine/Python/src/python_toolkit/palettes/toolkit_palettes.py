"""The toolkit's own palettes, and the matplotlib colour maps offered alongside them."""

from python_toolkit.palettes.palette import Palette

TOOLKIT_PALETTES: tuple[Palette, ...] = (
    Palette("okabe_ito", ("#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"),
            categorical=True, colourblind_safe=True),
    Palette("cool_to_warm", ("#3b4cc0", "#8db0fe", "#dddddd", "#f4987a", "#b40426")),
    Palette("traffic_light", ("#1a9850", "#fee08b", "#d73027")),
    Palette("ltc_heatmap", ("#000004", "#51127c", "#b63679", "#fb8861", "#fcffa4")),
    Palette("ltc_maya", ("#5c8286", "#a1b18c", "#e7cca6", "#d98f79", "#b35b5a")),
    Palette("ltc_paloma", ("#1a2a40", "#456a73", "#82a69d", "#d9ccb6", "#bf8865")),
    Palette("parula", ("#3e26a8", "#484cf0", "#337afd", "#21a3e3", "#14beb8", "#5ecd74", "#cbc128", "#fdcb32",
                       "#f9fb15")),
)

MATPLOTLIB_CATEGORICAL: tuple[str, ...] = (
    "Accent", "Dark2", "Paired", "Pastel1", "Pastel2", "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b", "tab20c",
)

MATPLOTLIB_CONTINUOUS: tuple[str, ...] = (
    "viridis", "plasma", "inferno", "magma", "cividis", "turbo", "Blues", "Greens", "Greys", "Oranges", "Purples",
    "Reds", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd", "coolwarm", "seismic", "Spectral", "RdYlBu", "RdYlGn", "twilight",
    "twilight_shifted", "hsv",
)

# perceptually uniform, so safe for the common colour vision deficiencies
MATPLOTLIB_COLOURBLIND_SAFE: tuple[str, ...] = ("viridis", "cividis", "plasma", "inferno", "magma")
