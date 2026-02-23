import tkinter as tk
from typing import Optional
from tkinter import ttk
import calendar
import datetime

class CalendarWidget(tk.Frame):
    def __init__(self, parent, def_year: int, def_month: int, def_day: int, show_year_selector: bool = False, year_min: int = 1900, year_max: int = 2100, item_title: Optional[str] = None, helper_text: Optional[str] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.year = def_year
        self.month = def_month
        self.show_year_selector = show_year_selector
        self.year_min = year_min
        self.year_max = year_max

        self.item_title = item_title
        self.helper_text = helper_text

        # Optional header/title label at the top of the widget
        if self.item_title:
            self.title_label = ttk.Label(self, text=self.item_title, style="Header.TLabel")
            self.title_label.pack(side="top", anchor="w")

        # Optional helper/requirements label above the input
        if self.helper_text:
            self.helper_label = ttk.Label(self, text=self.helper_text, style="Caption.TLabel")
            self.helper_label.pack(side="top", anchor="w")

        self.cal_frame = tk.Frame(self)
        self.cal_frame.pack(side="top", fill="x")

        self.month_frame = tk.Frame(self)
        self.month_frame.pack(side="top", fill="x")

        self.date_frame = tk.Frame(self)
        self.date_frame.pack(side="top", fill="x")

        if self.show_year_selector:
            self.year_selector()
        self.month_selector()
        self.set_day(def_day)
        self.redraw()

    def year_selector(self):
        year_var = tk.IntVar()
        year_var.set(self.year)

        years = list(range(self.year_min, self.year_max + 1))
        drop = tk.OptionMenu(self.month_frame, year_var, *years)
        year_var.trace_add("write", lambda *args: self.set_year(year_var))
        drop.pack(side="left", padx=4, pady=4)

    def month_selector(self):
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        clicked = tk.StringVar()
        clicked.set(self.months[self.month-1])

        drop = tk.OptionMenu(self.month_frame, clicked, *self.months)
        clicked.trace_add("write", lambda *args: self.set_month(clicked))
        drop.pack(side="left", padx=4, pady=4)

    def set_year(self, var):
        year = var.get()
        self.year = year
        self.redraw()

    def set_month(self, var):
        month = var.get()
        self.month = self.months.index(month) + 1
        self.redraw()

    def redraw(self):
        for child in self.cal_frame.winfo_children():
            child.destroy()

        for col, day in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
            label = tk.Label(self.cal_frame, text=day)
            label.grid(row=0, column=col, sticky="nsew")

        cal = calendar.monthcalendar(self.year, self.month)
        
        for row, week in enumerate(cal):
            for col, day in enumerate(week):
                text = "" if day == 0 else day
                state = "normal" if day > 0 else "disabled"
                cell = tk.Button(self.cal_frame, text=text, state=state, command=lambda day=day: self.set_day(day))
                cell.grid(row=row+1, column=col, sticky="nsew")
        
    def set_day(self, num):
        self.day = num

        for child in self.date_frame.winfo_children():
            child.destroy()

        date = self.months[self.month-1] + " " + str(self.day)
        label = tk.Label(self.date_frame, text=f"Selected Date: {date}")
        label.pack(padx=4, pady=4)
    
    def get_date(self):
        return datetime.date(self.year, self.month, self.day)
    
if __name__ == "__main__":

    from python_toolkit.tkinter.DefaultRoot import DefaultRoot

    root = DefaultRoot(min_height=500)
    root.title("Calendar Widget Test")

    # Example without year selector
    cal_widget1 = CalendarWidget(root.content_frame, def_year=2024, def_month=6, def_day=15, item_title="Select Start Date")
    cal_widget1.pack(padx=20, pady=20)

    root.mainloop()