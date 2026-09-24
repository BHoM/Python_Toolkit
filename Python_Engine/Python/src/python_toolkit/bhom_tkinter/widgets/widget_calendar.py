"""Calendar date-picker widget with optional year selector."""

import tkinter as tk
from typing import Optional, Literal
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
import calendar
import datetime

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets.drop_down_selection import DropDownSelection

class CalendarWidget(BHoMBaseWidget):
    """Render a month grid and allow date selection."""

    def __init__(
            self,
            parent: ttk.Frame, 
            def_year: int = 2026, 
            def_month: int = 1,
            def_day: int = 1,
            show_year_selector: bool = True,
            year_min: int = 1900,
            year_max: int = 2100,
            day_button_width: int = 4,
            day_button_padx: int = 1,
            day_button_pady: int = 1,
            day_button_text_alignment: Literal["left", "center", "right"] = "center",
            fixed_week_rows: int | None = None,
            selector_position: Literal["top", "bottom"] = "bottom",
            selection_label_format: Literal["short", "long"] = "short",
            **kwargs):
        
        super().__init__(parent, **kwargs)

        self.year = def_year
        self.month = def_month
        self.day = def_day
        self.show_year_selector = show_year_selector
        self.year_min = year_min
        self.year_max = year_max
        self.day_button_width = max(1, int(day_button_width))
        self.day_button_padx = int(day_button_padx)
        self.day_button_pady = int(day_button_pady)
        alignment_candidate = str(day_button_text_alignment).strip().lower()
        if alignment_candidate not in {"left", "center", "right"}:
            alignment_candidate = "center"
        self.day_button_text_alignment = alignment_candidate
        self.day_button_style = f"CalendarDay.{id(self)}.TButton"
        self.fixed_week_rows = (
            max(1, int(fixed_week_rows)) if fixed_week_rows is not None else None
        )
        selector_candidate = str(selector_position).strip().lower()
        self.selector_position = (
            selector_candidate if selector_candidate in {"top", "bottom"} else "bottom"
        )
        label_format = str(selection_label_format).strip().lower()
        self.selection_label_format = (
            label_format if label_format in {"short", "long"} else "short"
        )

        anchor_map = {
            "left": "w",
            "center": "center",
            "right": "e",
        }
        ttk.Style(self).configure(self.day_button_style, anchor=anchor_map[self.day_button_text_alignment])

        self.cal_frame = ttk.Frame(self.content_frame)
        self.month_frame = ttk.Frame(self.content_frame)
        self.date_frame = ttk.Frame(self.content_frame)

        if self.show_year_selector:
            self.year_selector()
        self.month_selector()
        self._pack_sections()
        self._initialized = False
        self._clamp_day()
        self.redraw()
        self._refresh_selection_label()
        self._initialized = True

    def year_selector(self):
        """Build the year dropdown selector."""
        years = [str(year) for year in range(self.year_min, self.year_max + 1)]
        self.year_dropdown = DropDownSelection(
            self.month_frame,
            options=years,
            default=str(self.year),
            command=lambda val: self.set_year(val),
            state="readonly",
        )
        self.year_dropdown.pack(side="left", padx=4, pady=4)

    def month_selector(self):
        """Build the month dropdown selector."""
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_dropdown = DropDownSelection(
            self.month_frame,
            options=self.months,
            default=self.months[self.month - 1],
            command=lambda val: self.set_month(val),
            state="readonly",
        )
        self.month_dropdown.pack(side="left", padx=4, pady=4)

    def _pack_sections(self) -> None:
        """Pack month selectors and calendar sections in the configured order."""
        for frame in (self.cal_frame, self.month_frame, self.date_frame):
            frame.pack_forget()

        if self.selector_position == "top":
            section_order = (self.month_frame, self.cal_frame, self.date_frame)
        else:
            section_order = (self.cal_frame, self.month_frame, self.date_frame)

        for frame in section_order:
            if frame is self.month_frame:
                frame.pack(side="top", anchor=self._pack_anchor, fill="x")
            else:
                frame.pack(side="top", fill="x")

    def _clamp_day(self) -> None:
        last_day = calendar.monthrange(self.year, self.month)[1]
        if self.day > last_day:
            self.day = last_day

    def _refresh_selection_label(self) -> None:
        for child in self.date_frame.winfo_children():
            child.destroy()

        try:
            selected = datetime.date(self.year, self.month, self.day)
            if self.selection_label_format == "long":
                text = f"Selected: {selected.strftime('%A %d %B %Y')}"
            else:
                text = f"Selected Date: {self.months[self.month - 1]} {self.day}"
        except ValueError as error:
            text = f"Selected: invalid date ({error})"

        label = Label(self.date_frame, text=text)
        self.align_child_text(label)
        label.pack(anchor=self._pack_anchor, padx=4, pady=4)

    def set_year(self, value):
        """Update the selected year and redraw the calendar.

        Args:
            value: The selected year as a string.
        """
        self.year = int(value)
        self._clamp_day()
        self.redraw()
        self._refresh_selection_label()

    def set_month(self, value):
        """Update the selected month and redraw the calendar.

        Args:
            value: The selected month name as a string.
        """
        self.month = self.months.index(value) + 1
        self._clamp_day()
        self.redraw()
        self._refresh_selection_label()

    def redraw(self):
        """Rebuild the month grid buttons for the current month and year."""
        for child in self.cal_frame.winfo_children():
            child.destroy()

        for col in range(7):
            self.cal_frame.columnconfigure(col, weight=1)

        for col, day in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            label = Label(self.cal_frame, text=day)
            self.align_child_text(label)
            label.grid(row=0, column=col, sticky="nsew")

        weeks = calendar.monthcalendar(self.year, self.month)
        if self.fixed_week_rows is not None:
            while len(weeks) < self.fixed_week_rows:
                weeks.append([0, 0, 0, 0, 0, 0, 0])
            weeks = weeks[: self.fixed_week_rows]
        
        for row, week in enumerate(weeks):
            for col, day in enumerate(week):
                text = "" if day == 0 else day
                state = "normal" if day > 0 else "disabled"
                cell_widget = Button(
                    self.cal_frame,
                    text=str(text) if text != "" else "",
                    command=(lambda d=day: self.set_day(d)),
                    width=self.day_button_width,
                )
                cell_widget.button.configure(style=self.day_button_style, state=state)
                cell_widget.grid(
                    row=row+1,
                    column=col,
                    sticky="nsew",
                    padx=self.day_button_padx,
                    pady=self.day_button_pady,
                )
        
    def set_day(self, num):
        """Set the selected day and refresh the date summary label.

        Args:
            num: Day of month to mark as selected.
        """
        if not num or num <= 0:
            return
        self.day = num
        self._refresh_selection_label()

        if self._initialized:
            self._fire_on_change(self.get())
    
    def get_date(self):
        """Return the selected date as a `datetime.date` instance.

        Returns:
            datetime.date: Currently selected date.
        """
        return datetime.date(self.year, self.month, self.day)
    
    def get(self):
        """Return the selected date value.

        Returns:
            datetime.date: Currently selected date.
        """
        return datetime.date(self.year, self.month, self.day)
    
    def set(self, value: datetime.date):
        """Set the selected date from a `datetime.date` value.

        Args:
            value: Date to apply to the widget.
        """
        self.year = value.year
        self.month = value.month
        self.day = value.day
        if hasattr(self, 'year_dropdown'):
            self.year_dropdown.set(str(self.year))
        if hasattr(self, 'month_dropdown'):
            self.month_dropdown.set(self.months[self.month - 1])
        self._clamp_day()
        self.redraw()
        self._refresh_selection_label()

    def validate(self) -> tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
        """Validate the currently selected date.

        Returns:
            tuple[bool, Optional[str], Optional[Literal['info', 'warning', 'error']]]:
                `(is_valid, message, severity)` where severity is `None` when
                valid, or `"error"` for an invalid date.
        """
        try:
            datetime.date(self.year, self.month, self.day)
            return self.apply_validation((True, None, None))
        except ValueError as ex:
            return self.apply_validation((False, f"Invalid date: {ex}", "error"))
    
    def pack(self, **kwargs):
        """Pack the widget and ensure the calendar grid is rendered.

        Args:
            **kwargs: Pack geometry manager options.
        """
        super().pack(**kwargs)
        self.redraw()
        
if __name__ == "__main__":

    from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
    from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

    root = BHoMBaseWindow(min_height=500, min_width=400, theme_mode="light")
    root.title("Calendar Widget Test")

    # Example without year selector
    cal_widget1 = CalendarWidget(
        root.content_frame,
        def_year=2024,
        def_month=6,
        def_day=15,
        day_button_width=2,
        day_button_padx=2,
        day_button_pady=2,
        day_button_text_alignment="center",
        item_title="Select a Date",
        helper_text="Choose a date from the calendar below.",
        build_options=PackingOptions(padx=20, pady=20)
    )
    cal_widget1.build()

    root.mainloop()
