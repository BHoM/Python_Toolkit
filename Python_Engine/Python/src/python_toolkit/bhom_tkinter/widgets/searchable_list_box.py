"""Scrollable listbox with a search filter that keeps selections while items are filtered out."""

from __future__ import annotations

import os
import re
import sys
import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, List, Literal, Optional

from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.list_box import ScrollableListBox

Scorer = Callable[[str, str], Optional[float]]  # (query, item) -> score (higher is better), or None for no match

_NON_ALNUM = re.compile(r"[\W_]+")
_BHOM_SEARCH = None  # (Compute, Scorer) from the BHoM Search_Engine, loaded on first use


def _load_bhom_search():
    """Load the BHoM Search_Engine through pythonnet the first time it is needed."""
    global _BHOM_SEARCH  # pylint: disable=global-statement
    if _BHOM_SEARCH is None:
        import clr  # pylint: disable=import-outside-toplevel,import-error

        sys.path.append(os.path.expandvars("%ProgramData%\\BHoM\\Assemblies"))
        clr.AddReference("Search_Engine")
        clr.AddReference("Search_oM")
        from BH.Engine.Search import Compute  # pylint: disable=import-outside-toplevel,import-error
        from BH.oM.Search import Scorer as BHoMScorer  # pylint: disable=import-outside-toplevel,import-error

        _BHOM_SEARCH = (Compute, BHoMScorer)
    return _BHOM_SEARCH


def default_scorer(query: str, text: str, min_score: float = 75) -> Optional[float]:
    """Score how well `query` matches `text` using the BHoM Search_Engine fuzzy match, or None if it is a weak match.

    Uses BH.Engine.Search.Compute.MatchScore with the WeightedRatio scorer. Case and punctuation are ignored.

    Args:
        query: The text typed into the filter.
        text: The item being tested.
        min_score: Similarity (0-100) an item needs to be shown. To use a different value, bind it with
            `functools.partial(default_scorer, min_score=...)` and pass that as `scorer`.
    """
    compute, bhom_scorer = _load_bhom_search()
    query = _NON_ALNUM.sub(" ", query.lower()).strip()
    text = _NON_ALNUM.sub(" ", text.lower()).strip()
    score = compute.MatchScore(query, text, bhom_scorer.WeightedRatio)
    return float(score) if score >= min_score else None


class SearchableListBox(BHoMBaseWidget):
    """A listbox with a filter entry beneath it, for picking from long lists.

    The filter sits in a row under the list.
    Typing in the filter narrows the list to fuzzy matches (typo-tolerant, case-insensitive), best first.
    Matching uses `default_scorer` (BHoM Search_Engine); pass `scorer` to use another algorithm.
    By default the selection is kept for items hidden by the filter, so several searches can build up one
    selection; `get()` always returns the full selection in item order.
    """

    def __init__(
            self,
            parent: ttk.Frame,
            items=None,
            selectmode=tk.MULTIPLE,
            height: int = 8,
            width: Optional[int] = None,
            show_selection_controls: bool = False,
            keep_hidden_selection: bool = True,
            show_summary: Optional[bool] = None,
            filter_label: str = "Filter",
            scorer: Scorer = default_scorer,
            **kwargs):
        """
        Args:
            parent (ttk.Frame): The parent widget.
            items (list, optional): Items to choose from.
            selectmode (str): tk.MULTIPLE / tk.EXTENDED for multi-select, tk.SINGLE / tk.BROWSE for one item.
            height (int): Visible rows in the list.
            width (int, optional): Width of the list in characters. If None, it expands to fill the space.
            show_selection_controls (bool): Show Select All / Deselect All buttons. They act on the items
                currently shown by the filter.
            keep_hidden_selection (bool): Keep items selected while the filter hides them. If False, the
                selection is limited to the visible items each time the filter changes.
            show_summary (bool, optional): Show a caption listing the selected items. Defaults to True for
                multi-select lists.
            filter_label (str): Caption shown above the filter entry.
            scorer (Callable): Called as scorer(query, item); returns a score (higher ranks first) or None to
                hide the item. Defaults to the BHoM Search_Engine fuzzy match.
            **kwargs: Additional BHoMBaseWidget / Frame options (id, item_title, helper_text, on_change, ...).
        """
        super().__init__(parent, **kwargs)

        self.scorer = scorer
        self._all_items: List[str] = [str(item) for item in (items or [])]
        self._shown: List[str] = list(self._all_items)
        self._multi = selectmode in (tk.MULTIPLE, tk.EXTENDED, "multiple", "extended")
        self._keep_hidden = bool(keep_hidden_selection)
        self._selected: set[str] = set()
        self._show_summary = self._multi if show_summary is None else bool(show_summary)

        self.filter_var = tk.StringVar()

        # List
        self.list_box = ScrollableListBox(
            self.content_frame,
            items=list(self._all_items),
            selectmode=selectmode,
            height=height,
            width=width,
            on_change=lambda _value: self._on_list_change(),
            build_options=PackingOptions(side="top", fill=tk.BOTH, expand=True),
        )
        self.list_box.build()

        # Filter entry
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(side="top", fill=tk.X, pady=(6, 0))
        ttk.Label(filter_frame, text=filter_label, style="Caption.TLabel").pack(side="top", anchor=self._pack_anchor)
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side="top", fill=tk.X, pady=(2, 0))
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())

        if show_selection_controls and self._multi:
            controls = ttk.Frame(self.content_frame)
            controls.pack(side="top", fill=tk.X, pady=(6, 0))
            controls.columnconfigure(0, weight=1)
            controls.columnconfigure(1, weight=1)
            ttk.Button(controls, text="Select All", command=self.select_all).grid(
                row=0, column=0, sticky="ew", padx=(0, 4))
            ttk.Button(controls, text="Deselect All", command=self.deselect_all).grid(
                row=0, column=1, sticky="ew", padx=(4, 0))

        self.summary_label: Optional[ttk.Label] = None
        if self._show_summary:
            self.summary_label = ttk.Label(self.content_frame, text="", style="Caption.TLabel", justify="left")
            self.summary_label.pack(side="top", anchor=self._pack_anchor, pady=(4, 0))
            self.content_frame.bind(
                "<Configure>", lambda e: self.summary_label.configure(wraplength=max(e.width - 4, 100)), add="+")
        self._update_summary()

    # ------------------------------------------------------------------ internals

    def _matching(self, query: str) -> List[str]:
        query = query.strip().lower()
        if not query:
            return list(self._all_items)
        scored = [(self.scorer(query, item), index, item) for index, item in enumerate(self._all_items)]
        return [item for score, index, item in sorted((s for s in scored if s[0] is not None),
                                                      key=lambda s: (-s[0], s[1]))]

    def _apply_filter(self) -> None:
        shown = self._matching(self.filter_var.get())
        self._shown = shown
        self.list_box.set_options(shown)
        if not self._keep_hidden:
            self._selected &= set(shown)
        self.list_box.set_selections([item for item in shown if item in self._selected])
        self._update_summary()
        if not self._keep_hidden:
            self._fire_on_change(self.get())

    def _on_list_change(self) -> None:
        visible = set(self.get_visible())
        chosen = set(self.list_box.get_selection())
        if self._multi:
            self._selected = (self._selected - visible) | chosen
        else:
            # Single select: a visible choice replaces the previous one; clicking away keeps it.
            if chosen:
                self._selected = chosen
        self._update_summary()
        self._fire_on_change(self.get())

    def _update_summary(self) -> None:
        if self.summary_label is None:
            return
        selected = self.get()
        visible = set(self.get_visible())
        hidden = [item for item in selected if item not in visible]
        if not selected:
            text = "None selected."
        else:
            text = f"{len(selected)} selected: {', '.join(selected)}"
            if hidden:
                text += f"  ({len(hidden)} hidden by the filter)"
        self.summary_label.configure(text=text)

    # ------------------------------------------------------------------ public API

    def get(self) -> List[str]:
        """Return all selected items (including any hidden by the filter), in item order."""
        return [item for item in self._all_items if item in self._selected]

    def get_selection(self) -> List[str]:
        """Alias of get() for parity with ScrollableListBox."""
        return self.get()

    def set(self, value) -> None:
        """Set the selection. Accepts one item, a list of items, or None to clear."""
        if value is None:
            wanted: Iterable[str] = []
        elif isinstance(value, (list, tuple, set)):
            wanted = [str(v) for v in value]
        else:
            wanted = [str(value)]
        wanted = [item for item in self._all_items if item in set(wanted)]
        if not self._multi:
            wanted = wanted[:1]
        self._selected = set(wanted)
        self.list_box.set_selections([item for item in self.get_visible() if item in self._selected])
        self._update_summary()
        self._fire_on_change(self.get())

    def get_options(self) -> List[str]:
        """Return every item, whatever the filter shows."""
        return list(self._all_items)

    def get_visible(self) -> List[str]:
        """Return the items currently shown by the filter."""
        return list(self._shown)

    def set_options(self, items) -> None:
        """Replace the items. Selected items that still exist stay selected."""
        self._all_items = [str(item) for item in (items or [])]
        self._selected &= set(self._all_items)
        self._apply_filter()
        self._fire_on_change(self.get())

    def set_filter(self, text: str) -> None:
        """Set the filter text (as if typed)."""
        self.filter_var.set(text or "")

    def get_filter(self) -> str:
        return self.filter_var.get()

    def clear_filter(self) -> None:
        self.set_filter("")

    def select_all(self) -> None:
        """Select every item currently shown by the filter."""
        if not self._multi:
            return
        self._selected |= set(self.get_visible())
        self.list_box.select_all()
        self._update_summary()
        self._fire_on_change(self.get())

    def deselect_all(self) -> None:
        """Deselect every item currently shown by the filter."""
        self._selected -= set(self.get_visible())
        self.list_box.deselect_all()
        self._update_summary()
        self._fire_on_change(self.get())

    def clear(self) -> None:
        """Deselect everything, including items hidden by the filter."""
        self._selected = set()
        self.list_box.deselect_all()
        self._update_summary()
        self._fire_on_change(self.get())

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """All states are valid unless a custom validation says otherwise."""
        return self.apply_validation((True, None, None))


if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow

    root = BHoMBaseWindow(title="SearchableListBox demo", theme_mode="light")
    widget = SearchableListBox(
        root.content_frame,
        items=[f"{city}_{kind}.epw" for city in ["London", "Birmingham", "Manchester", "Glasgow", "Belfast", "Cardiff"]
               for kind in ["TRY", "DSY1", "DSY2", "DSY3"]],
        height=8,
        width=40,
        show_selection_controls=True,
        item_title="Weather files",
        helper_text="Type to filter. Selections are kept while filtering.",
        on_change=lambda value: print("selected:", value),
        build_options=PackingOptions(padx=10, pady=10, fill="both", expand=True),
    )
    widget.build()
    root.mainloop()
