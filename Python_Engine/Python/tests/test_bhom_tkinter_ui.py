from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets import (
	Button,
	CalendarWidget,
	CheckboxSelection,
	CmapSelector,
	ColourPicker,
	DropDownSelection,
	FigureContainer,
	Label,
	MultiBoxSelection,
	PackingOptions,
	PathSelector,
	RadioSelection,
	ScrollableListBox,
	ValidatedEntryBox,
)
from python_toolkit.bhom_tkinter.windows import (
	DirectoryFileSelector,
	LandingPage,
	ProcessingWindow,
	WarningBox,
)


def _demo_callback(*_args, **_kwargs):
	return None


def _show_brief(window: BHoMBaseWindow, milliseconds: int = 900) -> None:
	window.after(milliseconds, window.destroy_root)
	window.mainloop()


def run_widget_gallery(auto_close_ms: int | None = None) -> None:
	root = BHoMBaseWindow(
		title="BHoM Tkinter Widget Gallery",
		min_width=1200,
		min_height=900,
		show_submit=False,
		show_close=True,
		close_text="Close Gallery",
	)

	parent = root.content_frame
	alignments = ["left", "center", "right"]

	Label(
		parent,
		text="Label widget (left)",
		item_title="Label",
		helper_text="Basic BHoM Label wrapper",
		alignment=alignments[0],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	Button(
		parent,
		text="Button widget",
		command=_demo_callback,
		item_title="Button",
		helper_text="Simple action button",
		alignment=alignments[1],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	ValidatedEntryBox(
		parent,
		item_title="ValidatedEntryBox",
		helper_text="Integer 0..100",
		value_type=int,
		min_value=0,
		max_value=100,
		alignment=alignments[2],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	DropDownSelection(
		parent,
		item_title="DropDownSelection",
		helper_text="Pick an option",
		options=["A", "B", "C"],
		default="B",
		alignment=alignments[0],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	RadioSelection(
		parent,
		item_title="RadioSelection",
		helper_text="Single select",
		fields=["Red", "Green", "Blue"],
		orient="horizontal",
		max_per_line=3,
		alignment=alignments[1],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	CheckboxSelection(
		parent,
		item_title="CheckboxSelection",
		helper_text="Multi select",
		fields=["One", "Two", "Three", "Four"],
		defaults=["Two"],
		max_per_line=4,
		alignment=alignments[2],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	MultiBoxSelection(
		parent,
		item_title="MultiBoxSelection",
		helper_text="Legacy alias variant",
		fields=["North", "South", "East", "West"],
		orient="horizontal",
		max_per_line=2,
		alignment=alignments[0],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	ScrollableListBox(
		parent,
		item_title="ScrollableListBox",
		helper_text="List with selection controls",
		items=[f"Item {i}" for i in range(1, 13)],
		height=5,
		show_selection_controls=True,
		alignment=alignments[1],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	PathSelector(
		parent,
		item_title="PathSelector",
		helper_text="Browse file path",
		button_text="Browse",
		mode="file",
		alignment=alignments[2],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	ColourPicker(
		parent,
		item_title="ColourPicker",
		helper_text="Pick a colour",
		default_colour="#4A90E2",
		alignment=alignments[0],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	CalendarWidget(
		parent,
		item_title="CalendarWidget",
		helper_text="Date picker",
		def_year=date.today().year,
		def_month=date.today().month,
		def_day=max(1, min(date.today().day, 28)),
		show_year_selector=True,
		alignment=alignments[1],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	figure_container = FigureContainer(
		parent,
		item_title="FigureContainer",
		helper_text="Embedded matplotlib figure",
		alignment=alignments[2],
		packing_options=PackingOptions(fill="x", pady=6),
	)
	figure_container.build()
	figure, axis = plt.subplots(figsize=(3.2, 1.2))
	axis.plot([0, 1, 2, 3], [1, 3, 2, 4])
	axis.set_title("Sample")
	figure_container.embed_figure(figure)

	CmapSelector(
		parent,
		item_title="CmapSelector",
		helper_text="Colormap preview",
		cmap_set="continuous",
		alignment=alignments[0],
		packing_options=PackingOptions(fill="x", pady=6),
	).build()

	if auto_close_ms is not None:
		root.after(auto_close_ms, root.destroy_root)
	root.mainloop()


def run_predefined_windows_demo() -> None:
	landing = LandingPage(
		title="LandingPage demo",
		header="Landing page",
		message="Smoke-checking predefined windows.",
		sub_title="This window auto-closes.",
		show_submit=False,
	)
	landing.add_custom_button("No-op Action", _demo_callback)
	_show_brief(landing)

	warning = WarningBox(
		title="WarningBox demo",
		warnings=["Sample warning message"],
		errors=["Sample error message"],
		infos=["Sample informational message"],
	)
	_show_brief(warning)

	processing = ProcessingWindow(title="ProcessingWindow demo", message="Working...")
	processing.start()
	processing.after(900, processing.stop)
	processing.mainloop()

	selector = DirectoryFileSelector(
		directory=Path(__file__).resolve().parent,
		file_types=[".py"],
		selection_label="test files",
	)
	_show_brief(selector)


if __name__ == "__main__":
	run_widget_gallery()
	run_predefined_windows_demo()
