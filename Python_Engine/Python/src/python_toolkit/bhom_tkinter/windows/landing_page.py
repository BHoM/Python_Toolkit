"""Landing page window with configurable header, message text, and custom actions."""

from tkinter import ttk
from typing import Optional, Callable
from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
from python_toolkit.bhom_tkinter.widgets.button import Button
from python_toolkit.bhom_tkinter.widgets.label import Label
from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions


class LandingPage(BHoMBaseWindow):
    """
    A reusable landing page GUI with configurable title, message, and buttons.
    Uses BHoMBaseWindow as the base template.
    """

    def __init__(
        self,
        title: str = "Landing Page",
        header: Optional[str] = None,
        message: Optional[str] = None,
        sub_title: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes the landing page GUI.

        Args:
            title (str): Window and header title text.
            message (str, optional): Commentary/message text to display.
        """
        self.header = header
        self.message = message
        self.sub_title = sub_title
        self.custom_buttons_frame: Optional[ttk.Frame] = None

        super().__init__(
            title=title,
            **kwargs,
        )

    def build(self):
        """Build landing-page content using the base window's content area."""
        if self.header:
            header_label = Label(
                self.content_frame,
                text=self.header,
                style="Headline.TLabel",
                alignment="left",
                build_options=PackingOptions(side="top", anchor="w", pady=(0, 10)),
            )
            header_label.build()

        if self.message:
            message_label = Label(
                self.content_frame,
                text=self.message,
                style="Body.TLabel",
                justify="left",
                alignment="left",
                build_options=PackingOptions(side="top", anchor="w", pady=(0, 10)),
            )
            message_label.build()
        
        if self.sub_title:
            sub_title_label = Label(
                self.content_frame,
                text=self.sub_title,
                style="Caption.TLabel",
                alignment="left",
                build_options=PackingOptions(side="top", anchor="w", pady=(0, 10)),
            )
            sub_title_label.build()

        self.custom_buttons_frame = ttk.Frame(self.content_frame)
        self.custom_buttons_frame.pack(fill="x", pady=(0, 20))

        super().build()

    def add_custom_button(self, text: str, command: Callable, **kwargs) -> ttk.Button:
        """
        Add a custom button to the landing page.

        Args:
            text (str): Button text.
            command (callable): Function to call when button is clicked.
            **kwargs: Additional ttk.Button options.

        Returns:
            ttk.Button: The created button widget.
        """
        if self.custom_buttons_frame is None:
            self.custom_buttons_frame = ttk.Frame(self.content_frame)
            self.custom_buttons_frame.pack(fill="x", pady=(0, 20))

        button_widget = Button(self.custom_buttons_frame, text=text, command=command, **kwargs)
        button_widget.pack(pady=5, fill="x")
        # Recalculate window size after adding button
        self.refresh_sizing()
        # Return inner ttk.Button for compatibility
        return button_widget.button


if __name__ == "__main__":

    #simple example of using the landing page
    def on_button_click():
        """Handle demo button clicks in the standalone example."""
        print("Button clicked!")
    
    def on_button_click_2():
        """Handle demo button clicks in the standalone example."""
        print("Second button clicked!")

    landing_page = LandingPage(
        title="Welcome to the BHoM Toolkit",
        header="Welcome to the BHoM Toolkit",
        message="This is a landing page example. You can add custom buttons below.",
        sub_title="Please click the button to proceed.",
        show_close=True,
        show_submit=False,
    )
    landing_page.add_custom_button(text="Click Me", command=on_button_click)
    landing_page.add_custom_button(text="Click Me 2", command=on_button_click_2)
    landing_page.mainloop()