"""Calendar date-picker widget with optional year selector."""

import tkinter as tk
from typing import Optional, Literal
from tkinter import ttk
from python_toolkit.bhom_tkinter.widgets.label import Label
import calendar
import datetime

from python_toolkit.bhom_tkinter.widgets._widgets_base import BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.button import Button

class CalendarWidget(BHoMBaseWidget):
    """Render a month grid and allow date selection."""

    def __init__(
            self,
            parent: ttk.Frame, 
            def_year: int, 
            def_month: int, 
            def_day: int,
            show_year_selector: bool = True,
            year_min: int = 1900,
            year_max: int = 2100,
            day_button_width: int = 4,
            day_button_padx: int = 1,
            day_button_pady: int = 1,
            day_button_text_alignment: Literal["left", "center", "right"] = "center",
            **kwargs):
        
        super().__init__(parent, **kwargs)

        self.year = def_year
        self.month = def_month
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

        anchor_map = {
            "left": "w",
            "center": "center",
            "right": "e",
        }
        ttk.Style(self).configure(self.day_button_style, anchor=anchor_map[self.day_button_text_alignment])

        self.cal_frame = ttk.Frame(self.content_frame)
        self.cal_frame.pack(side="top", fill="x")

        self.month_frame = ttk.Frame(self.content_frame)
        self.month_frame.pack(side="top", fill="x")

        self.date_frame = ttk.Frame(self.content_frame)
        self.date_frame.pack(side="top", fill="x")

        if self.show_year_selector:
            self.year_selector()
        self.month_selector()
        self.set_day(def_day)
        self.redraw()

    def year_selector(self):
        """Build the year dropdown selector."""
        year_var = tk.StringVar()
        year_var.set(str(self.year))

        years = [str(year) for year in range(self.year_min, self.year_max + 1)]
        drop = tk.OptionMenu(self.month_frame, year_var, *years)
        year_var.trace_add("write", lambda *args: self.set_year(year_var))
        drop.pack(side="left", padx=4, pady=4)

    def month_selector(self):
        """Build the month dropdown selector."""
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        clicked = tk.StringVar()
        clicked.set(self.months[self.month-1])

        drop = tk.OptionMenu(self.month_frame, clicked, *self.months)
        clicked.trace_add("write", lambda *args: self.set_month(clicked))
        drop.pack(side="left", padx=4, pady=4)

    def set_year(self, var):
        """Update the selected year and redraw the calendar.

        Args:
            var: Tk variable containing the selected year.
        """
        year = int(var.get())
        self.year = year
        self.redraw()

    def set_month(self, var):
        """Update the selected month and redraw the calendar.

        Args:
            var: Tk variable containing the selected month name.
        """
        month = var.get()
        self.month = self.months.index(month) + 1
        self.redraw()

    def redraw(self):
        """Rebuild the month grid buttons for the current month and year."""
        for child in self.cal_frame.winfo_children():
            child.destroy()

        for col, day in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            label = Label(self.cal_frame, text=day)
            getattr(self, "align_child_text")(label)
            label.grid(row=0, column=col, sticky="nsew")

        cal = calendar.monthcalendar(self.year, self.month)
        
        for row, week in enumerate(cal):
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
        self.day = num

        for child in self.date_frame.winfo_children():
            child.destroy()

        date = self.months[self.month-1] + " " + str(self.day)
        label = Label(self.date_frame, text=f"Selected Date: {date}")
        getattr(self, "align_child_text")(label)
        label.pack(anchor=getattr(self, "_pack_anchor"), padx=4, pady=4)
    
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
        self.redraw()

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

    root = BHoMBaseWindow(min_height=500)
    root.title("Calendar Widget Test")

    # Example without year selector
    cal_widget1 = CalendarWidget(
        root.content_frame,
        def_year=2024,
        def_month=6,
        def_day=15,
        day_button_width=3,
        day_button_padx=2,
        day_button_pady=2,
        day_button_text_alignment="center",
        item_title="Select a Date",
        helper_text="Choose a date from the calendar below.",
        packing_options=PackingOptions(padx=20, pady=20)
    )
    cal_widget1.build()

    root.mainloop()