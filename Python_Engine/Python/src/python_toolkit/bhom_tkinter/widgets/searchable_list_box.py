"""Scrollable listbox with a search filter that keeps selections while items are filtered out."""

from __future__ import annotations

import difflib
import re
import tkinter as tk
from tkinter import ttk
from typing import Iterable, List, Literal, Optional

from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions
from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets.list_box import ScrollableListBox

_WORD_SPLIT = re.compile(r"[\s_\-\.\(\)\[\],/\\]+")
_TYPO_MIN_LENGTH = 4       # query words shorter than this must match exactly or as a subsequence
_TYPO_MIN_RATIO = 0.8      # difflib similarity needed to accept a misspelt word
_TYPO_MAX_LENGTH_DIFF = 2  # a misspelling may be at most this many letters longer/shorter than the word


def _subsequence_gaps(token: str, text: str) -> Optional[int]:
    """Characters skipped to find token's letters in order in text, or None if they are not all there."""
    position, gaps = 0, 0
    for char in token:
        found = text.find(char, position)
        if found < 0:
            return None
        gaps += found - position
        position = found + 1
    return gaps


def fuzzy_score(query: str, text: str) -> Optional[float]:
    """Score how well `query` matches `text` (higher is better), or None if it does not match.

    Every whitespace-separated word of the query must match the text, in one of these ways (best first):
        - contained in the text, with a bonus when it starts a word ("lon" in "London_TRY")
        - its letters appear in order with only small gaps ("ldn" in "London"), scored down by the gaps
        - a close misspelling of one of the text's words ("birmigham" for "Birmingham"), words of 4+ letters
    An empty query matches everything with score 0.
    """
    text_l = text.lower()
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return 0.0
    words = [w for w in _WORD_SPLIT.split(text_l) if w]
    score = 0.0
    for token in tokens:
        index = text_l.find(token)
        if index >= 0:
            starts_word = index == 0 or not text_l[index - 1].isalnum()
            score += 100 + (20 if starts_word else 0) - min(index, 20) * 0.5
            continue
        gaps = _subsequence_gaps(token, text_l)
        # Letters in order only count when they are close together, otherwise short words match almost anything.
        if gaps is not None and gaps <= max(3, len(token)):
            score += max(60 - gaps * 4, 20)
            continue
        similar = [w for w in words if abs(len(w) - len(token)) <= _TYPO_MAX_LENGTH_DIFF]
        if len(token) >= _TYPO_MIN_LENGTH and similar:
            ratio = max(difflib.SequenceMatcher(None, token, w).ratio() for w in similar)
            if ratio >= _TYPO_MIN_RATIO:
                score += ratio * 50
                continue
        return None
    return score


class SearchableListBox(BHoMBaseWidget):
    """A listbox with a filter entry above it, for picking from long lists.

    Typing in the filter narrows the list. With match_mode="fuzzy" (default) each typed word may match as
    a substring, as letters in order, or as a close misspelling, and the best matches are listed first
    (see `fuzzy_score`). With match_mode="contains" the list shows items containing the text, in order.
    Matching is case-insensitive. By default the selection is kept for items hidden by the filter, so
    several searches can build up one selection; `get()` always returns the full selection in item order.
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
            filter_label: str = "Search",
            match_mode: Literal["fuzzy", "contains"] = "fuzzy",
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
            match_mode (str): "fuzzy" (typo-tolerant, best matches first) or "contains" (plain substring).
            **kwargs: Additional BHoMBaseWidget / Frame options (id, item_title, helper_text, on_change, ...).
        """
        super().__init__(parent, **kwargs)

        if match_mode not in ("fuzzy", "contains"):
            raise ValueError(f"match_mode must be 'fuzzy' or 'contains', not {match_mode!r}")
        self.match_mode = match_mode
        self._all_items: List[str] = [str(item) for item in (items or [])]
        self._multi = selectmode in (tk.MULTIPLE, tk.EXTENDED, "multiple", "extended")
        self._keep_hidden = bool(keep_hidden_selection)
        self._selected: set[str] = set()
        self._show_summary = self._multi if show_summary is None else bool(show_summary)

        # Filter entry
        filter_frame = ttk.Frame(self.content_frame)
        filter_frame.pack(side="top", fill=tk.X)
        ttk.Label(filter_frame, text=filter_label, style="Caption.TLabel").pack(side="top", anchor=self._pack_anchor)
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var)
        self.filter_entry.pack(side="top", fill=tk.X, pady=(2, 6))
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())

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

        if show_selection_controls and self._multi:
            controls = ttk.Frame(self.content_frame)
            controls.pack(side="top", fill=tk.X, pady=(6, 0))
            controls.columnconfigure(0, weight=1)
            controls.columnconfigure(1, weight=1)
            select_widget = Button(controls, text="Select All", command=self.select_all)
            select_widget.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            deselect_widget = Button(controls, text="Deselect All", command=self.deselect_all)
            deselect_widget.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self.summary_label: Optional[ttk.Label] = None
        if self._show_summary:
            self.summary_label = ttk.Label(self.content_frame, text="", style="Caption.TLabel", justify="left")
            self.summary_label.pack(side="top", anchor=self._pack_anchor, pady=(4, 0))
            self.content_frame.bind(
                "<Configure>", lambda e: self.summary_label.configure(wraplength=max(e.width - 4, 100)), add="+")
        self._update_summary()

    # ------------------------------------------------------------------ internals

    def _visible(self) -> List[str]:
        return self.list_box.get_options()

    def _matching(self, query: str) -> List[str]:
        query = query.strip().lower()
        if not query:
            return list(self._all_items)
        if self.match_mode == "contains":
            return [item for item in self._all_items if query in item.lower()]
        scored = [(fuzzy_score(query, item), index, item) for index, item in enumerate(self._all_items)]
        return [item for score, index, item in sorted((s for s in scored if s[0] is not None),
                                                      key=lambda s: (-s[0], s[1]))]

    def _apply_filter(self) -> None:
        shown = self._matching(self.filter_var.get())
        self.list_box.set_options(shown)
        if not self._keep_hidden:
            self._selected &= set(shown)
        self.list_box.set_selections([item for item in shown if item in self._selected])
        self._update_summary()
        if not self._keep_hidden:
            self._fire_on_change(self.get())

    def _on_list_change(self) -> None:
        visible = set(self._visible())
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
        hidden = [item for item in selected if item not in set(self._visible())]
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
        self.list_box.set_selections([item for item in self._visible() if item in self._selected])
        self._update_summary()
        self._fire_on_change(self.get())

    def get_options(self) -> List[str]:
        """Return every item, whatever the filter shows."""
        return list(self._all_items)

    def get_visible(self) -> List[str]:
        """Return the items currently shown by the filter."""
        return self._visible()

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
        self._selected |= set(self._visible())
        self.list_box.select_all()
        self._update_summary()
        self._fire_on_change(self.get())

    def deselect_all(self) -> None:
        """Deselect every item currently shown by the filter."""
        self._selected -= set(self._visible())
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
