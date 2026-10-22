from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import tkinter as tk

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
	SearchableListBox,
	ValidatedEntryBox,
)
from python_toolkit.bhom_tkinter.windows import (
	DirectoryFileSelector,
	LandingPage,
	ProcessingWindow,
	WarningBox,
)
from python_toolkit.bhom_tkinter.bhom_base_child_window import BHoMBaseChildWindow
from python_toolkit.bhom_tkinter.windows.modal_window import BHoMModalWindow


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
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	Button(
		parent,
		text="Button widget",
		command=_demo_callback,
		item_title="Button",
		helper_text="Simple action button",
		alignment=alignments[1],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	ValidatedEntryBox(
		parent,
		item_title="ValidatedEntryBox",
		helper_text="Integer 0..100",
		value_type=int,
		min_value=0,
		max_value=100,
		alignment=alignments[2],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	DropDownSelection(
		parent,
		item_title="DropDownSelection",
		helper_text="Pick an option",
		options=["A", "B", "C"],
		default="B",
		alignment=alignments[0],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	RadioSelection(
		parent,
		item_title="RadioSelection",
		helper_text="Single select",
		fields=["Red", "Green", "Blue"],
		orient="horizontal",
		max_per_line=3,
		alignment=alignments[1],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	CheckboxSelection(
		parent,
		item_title="CheckboxSelection",
		helper_text="Multi select",
		fields=["One", "Two", "Three", "Four"],
		defaults=["Two"],
		max_per_line=4,
		alignment=alignments[2],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	MultiBoxSelection(
		parent,
		item_title="MultiBoxSelection",
		helper_text="Legacy alias variant",
		fields=["North", "South", "East", "West"],
		orient="horizontal",
		max_per_line=2,
		alignment=alignments[0],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	ScrollableListBox(
		parent,
		item_title="ScrollableListBox",
		helper_text="List with selection controls",
		items=[f"Item {i}" for i in range(1, 13)],
		height=5,
		show_selection_controls=True,
		alignment=alignments[1],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	SearchableListBox(
		parent,
		item_title="SearchableListBox",
		helper_text="Type to filter; selections are kept while filtering",
		items=[f"{city}_TRY.epw" for city in ["London", "Birmingham", "Manchester", "Glasgow", "Belfast", "Cardiff"]],
		height=4,
		show_selection_controls=True,
		alignment=alignments[2],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	PathSelector(
		parent,
		item_title="PathSelector",
		helper_text="Browse file path",
		button_text="Browse",
		mode="file",
		alignment=alignments[2],
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	ColourPicker(
		parent,
		item_title="ColourPicker",
		helper_text="Pick a colour",
		default_colour="#4A90E2",
		alignment=alignments[0],
		build_options=PackingOptions(fill="x", pady=6),
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
		build_options=PackingOptions(fill="x", pady=6),
	).build()

	figure_container = FigureContainer(
		parent,
		item_title="FigureContainer",
		helper_text="Embedded matplotlib figure",
		alignment=alignments[2],
		build_options=PackingOptions(fill="x", pady=6),
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
		build_options=PackingOptions(fill="x", pady=6),
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


def test_widget_validation():
	"""Ensure widget validation logic returns expected results."""
	# Integer field valid range
	root = BHoMBaseWindow(title="Validation test")
	parent = root.content_frame

	int_box = ValidatedEntryBox(
		parent,
		value_type=int,
		min_value=0,
		max_value=100,
		required=True,
	)
	int_box.build()

	int_box.set(50)
	ok, msg, sev = int_box.validate()
	assert ok is True and msg is None

	int_box.set(150)
	ok, msg, sev = int_box.validate()
	assert ok is False and sev == "error"

	# Required field empty
	int_box.set("")
	ok, msg, sev = int_box.validate()
	assert ok is False and msg == "Required"

	# Non-required empty is valid
	opt_box = ValidatedEntryBox(parent, value_type=str, required=False)
	opt_box.build()
	opt_box.set("")
	ok, msg, sev = opt_box.validate()
	assert ok is True

	# Custom validator overriding
	def fail_validator(_v):
		return False, "Custom failed"

	custom_box = ValidatedEntryBox(parent, value_type=str, required=True, custom_validator=fail_validator)
	custom_box.build()
	custom_box.set("abc")
	ok, msg, sev = custom_box.validate()
	assert ok is False and msg == "Custom failed"


def test_rebuild():
	"""Verify that rebuild() re-places widgets and reflects mutations to self.widgets."""
	root = BHoMBaseWindow(title="Rebuild test")
	parent = root.content_frame

	label_a = Label(parent, text="Widget A", build_options=PackingOptions(fill="x"))
	label_b = Label(parent, text="Widget B", build_options=PackingOptions(fill="x"))

	root.widgets.extend([label_a, label_b])
	root.build()

	# Both widgets should be managed after build
	managed_after_build = [
		c for c in parent.winfo_children() if c.winfo_manager()
	]
	assert len(managed_after_build) == 2

	# Add a third widget and rebuild
	label_c = Label(parent, text="Widget C", build_options=PackingOptions(fill="x"))
	root.widgets.append(label_c)
	root.rebuild()

	managed_after_rebuild = [
		c for c in parent.winfo_children() if c.winfo_manager()
	]
	assert len(managed_after_rebuild) == 3

	# Remove a widget and rebuild — it should no longer be managed
	root.widgets.remove(label_a)
	root.rebuild()

	managed_after_remove = [
		c for c in parent.winfo_children() if c.winfo_manager()
	]
	assert len(managed_after_remove) == 2
	assert label_a not in [w for w in root.widgets]

	root.destroy_root()


def test_modal_window_is_themed_toplevel():
	"""Modal windows should be themed Toplevels, not tk.Tk roots."""
	host = BHoMBaseWindow(title="Modal host", show_submit=False, show_close=False)
	host.withdraw()

	modal = BHoMModalWindow(
		host,
		title="Modal test",
		width=420,
		height=260,
		show_close=True,
	)
	assert isinstance(modal, tk.Toplevel)
	assert isinstance(modal, BHoMBaseChildWindow)
	assert hasattr(modal, "content_frame")
	assert not isinstance(modal, BHoMBaseWindow)

	Label(
		modal.content_frame,
		text="Modal body",
		build_options=PackingOptions(anchor="w"),
	).build()
	modal.update_idletasks()
	assert modal.winfo_exists()

	modal.close()
	host.destroy_root()


def test_searchable_list_box():
	"""Selections survive filtering; select/deselect all act on visible items; single mode keeps one item."""
	root = BHoMBaseWindow(title="SearchableListBox test")
	changes = []
	items = ["London_TRY.epw", "London_DSY1.epw", "Gibraltar_TRY.epw", "Belfast_TRY.epw"]

	box = SearchableListBox(root.content_frame, items=items, show_selection_controls=True,
							on_change=lambda value: changes.append(list(value)))
	box.build()

	# Build a selection across two searches
	box.set_filter("gib")
	assert box.get_visible() == ["Gibraltar_TRY.epw"]
	box.list_box.set_selections(["Gibraltar_TRY.epw"])
	box._on_list_change()
	box.set_filter("belfast")
	box.list_box.set_selections(["Belfast_TRY.epw"])
	box._on_list_change()
	assert box.get() == ["Gibraltar_TRY.epw", "Belfast_TRY.epw"]
	assert changes[-1] == ["Gibraltar_TRY.epw", "Belfast_TRY.epw"]

	# Clearing the filter shows the hidden selections as selected
	box.clear_filter()
	assert box.get_visible() == items
	assert box.list_box.get_selection() == ["Gibraltar_TRY.epw", "Belfast_TRY.epw"]

	# Select/deselect all only affect visible items
	box.set_filter("london")
	box.select_all()
	assert box.get() == items
	box.deselect_all()
	assert box.get() == ["Gibraltar_TRY.epw", "Belfast_TRY.epw"]

	# set / clear / set_options
	box.set(["London_TRY.epw"])
	assert box.get() == ["London_TRY.epw"]
	box.clear()
	assert box.get() == []
	box.set(items)
	box.set_options(["London_TRY.epw", "Cardiff_TRY.epw"])
	assert box.get() == ["London_TRY.epw"]

	# keep_hidden_selection=False drops selections the filter hides
	strict = SearchableListBox(root.content_frame, items=items, keep_hidden_selection=False)
	strict.build()
	strict.set(["London_TRY.epw", "Belfast_TRY.epw"])
	strict.set_filter("london")
	assert strict.get() == ["London_TRY.epw"]

	# Single select keeps at most one item, and a hidden choice survives filtering
	single = SearchableListBox(root.content_frame, items=items, selectmode=tk.SINGLE)
	single.build()
	single.set(items)
	assert single.get() == ["London_TRY.epw"]
	single.set_filter("gib")
	assert single.get() == ["London_TRY.epw"]
	single.list_box.set_selections(["Gibraltar_TRY.epw"])
	single._on_list_change()
	assert single.get() == ["Gibraltar_TRY.epw"]

	root.destroy_root()


def test_searchable_list_box_fuzzy_matching():
	"""Fuzzy mode: substrings, close letter sequences and typos match, best first; contains mode is plain."""
	from python_toolkit.bhom_tkinter.widgets.searchable_list_box import fuzzy_score

	assert fuzzy_score("", "anything") == 0.0
	assert fuzzy_score("lon", "London_TRY.epw") is not None
	assert fuzzy_score("ldn try", "London_TRY.epw") is not None      # letters in order, per word
	assert fuzzy_score("birmigham", "Birmingham_TRY.epw") is not None  # typo
	assert fuzzy_score("xyzq", "London_TRY.epw") is None
	assert fuzzy_score("try", "NZL_Taranaki_New_Plymouth.epw") is None  # letters too far apart
	assert fuzzy_score("london", "LOS-ANGELES-DOWNTOWN.epw") is None    # not a close misspelling
	# Whole-word start beats a match inside a word
	assert fuzzy_score("try", "London_TRY.epw") > fuzzy_score("try", "Country.epw")

	root = BHoMBaseWindow(title="SearchableListBox fuzzy test")
	items = ["Country_Club.epw", "London_TRY.epw", "Birmingham_TRY.epw", "Gibraltar_TRY.epw"]

	fuzzy = SearchableListBox(root.content_frame, items=items)
	fuzzy.build()
	fuzzy.set_filter("birmigham")
	assert fuzzy.get_visible() == ["Birmingham_TRY.epw"]
	fuzzy.set_filter("try")
	# Word-start matches rank above the match inside "Country" (earlier matches rank slightly higher)
	assert set(fuzzy.get_visible()[:3]) == {"London_TRY.epw", "Birmingham_TRY.epw", "Gibraltar_TRY.epw"}
	assert fuzzy.get_visible()[-1] == "Country_Club.epw"

	contains = SearchableListBox(root.content_frame, items=items, match_mode="contains")
	contains.build()
	contains.set_filter("birmigham")
	assert contains.get_visible() == []
	contains.set_filter("try")
	assert contains.get_visible() == items  # "Country" contains "try"; original order kept

	root.destroy_root()
