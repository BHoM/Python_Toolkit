"""Typography style guide and verification sample.

Run directly:
    python tests/test_styling.py

This opens a guide window with one label sample per typography style so it can
be used both as a visual reference and as a quick regression check.
"""

from __future__ import annotations

import os
from tkinter import ttk
from tkinter import font as tkfont

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets.label import Label as BHoMLabel


def _style_rows() -> list[tuple[str, str]]:
    return [
        ("Display.TLabel", "Display — 0123456789"),
        ("LargeTitle.TLabel", "LargeTitle sample"),
        ("Title.TLabel", "Title sample"),
        ("Headline.TLabel", "Headline sample"),
        ("Subtitle.TLabel", "Subtitle sample"),
        ("Heading.TLabel", "Heading sample"),
        ("Body.TLabel", "Body sample"),
        ("TLabel", "TLabel sample"),
        ("Caption.TLabel", "Caption sample"),
        ("Small.TLabel", "Small sample"),
        ("Success.TLabel", "Success sample"),
        ("Warning.TLabel", "Warning sample"),
        ("Error.TLabel", "Error sample"),
        ("Info.TLabel", "Info sample"),
    ]


def run_styling_guide(
    theme_mode: str = "dark",
    print_metrics: bool = True,
    auto_close_ms: int | None = None,
) -> None:
    os.environ.setdefault("BHOM_TK_DEBUG_STYLES", "1")

    window = BHoMBaseWindow(
        title="Typography Style Guide",
        theme_mode=theme_mode,
        show_submit=False,
        show_close=True,
        top_most=False,
        min_width=780,
        min_height=700,
    )

    style = ttk.Style()
    rows = _style_rows()

    BHoMLabel(
        window.content_frame,
        text="Typography Guide (BHoM Label wrapper)",
        style="Title.TLabel",
    ).pack(anchor="w", pady=(2, 10))

    BHoMLabel(
        window.content_frame,
        text=f"Theme: {style.theme_use()}",
        style="Caption.TLabel",
    ).pack(anchor="w", pady=(0, 12))

    guide_rows: list[tuple[str, BHoMLabel]] = []
    for style_name, sample_text in rows:
        row = ttk.Frame(window.content_frame)
        row.pack(fill="x", anchor="w", pady=2)

        style_tag = BHoMLabel(row, text=style_name, style="Caption.TLabel", width=22)
        style_tag.pack(side="left", anchor="w", padx=(0, 10))

        sample = BHoMLabel(row, text=sample_text, style=style_name)
        sample.pack(side="left", anchor="w")
        guide_rows.append((style_name, sample))

    window.update_idletasks()

    if print_metrics:
        print("theme", style.theme_use())
        print("--- typography styles ---")
        for style_name, sample in guide_rows:
            font_lookup = style.lookup(style_name, "font") or style.lookup("TLabel", "font")
            parsed = tkfont.Font(root=window, font=font_lookup)
            print(
                style_name,
                "lookup=", font_lookup,
                "actual-size=", parsed.actual("size"),
                "linespace=", parsed.metrics("linespace"),
                "rendered-height=", sample.label.winfo_reqheight(),
            )

    if auto_close_ms is not None and auto_close_ms > 0:
        window.after(auto_close_ms, window.destroy)

    window.mainloop()


if __name__ == "__main__":
    run_styling_guide()
