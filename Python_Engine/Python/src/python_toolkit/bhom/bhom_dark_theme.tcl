# Dark and Light Mode Theme for Python Toolkit
# Professional themes inspired by modern IDEs
# Font: Segoe UI, Roboto, Helvetica, Arial, sans-serif

# ============================================================================
# DARK MODE THEME
# ============================================================================

# Split theme file generated from bhom_style.tcl
namespace eval ttk::theme::bhom_dark {
    variable colors
    array set colors {
        -bg             "#1e1e1e"
        -fg             "#ffffff"
        -dark           "#2d2d2d"
        -darker         "#252526"
        -selectbg       "#1b6ec2"
        -selectfg       "#ffffff"
        -primary        "#1b6ec2"
        -primary-hover  "#1861ac"
        -primary-light  "#258cfb"
        -secondary      "#ff4081"
        -secondary-hover "#ff1f69"
        -tertiary       "#c4d600"
        -info           "#006bb7"
        -success        "#26b050"
        -warning        "#eb671c"
        -error          "#e50000"
        -border         "#3d3d3d"
        -border-light   "#555555"
        -disabled-bg    "#2d2d2d"
        -disabled-fg    "#666666"
        -inputbg        "#2d2d2d"
        -inputfg        "#ffffff"
        -hover-bg       "#2a2d2e"
        -active-bg      "#383838"
        -text-secondary "#999999"
    }

    ttk::style theme create bhom_dark -parent clam -settings {
        # General font settings - Segoe UI for Windows, fallback to Roboto/Helvetica
        ttk::style configure . \
            -font {{Segoe UI} 10} \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-border) \
            -darkcolor $colors(-border) \
            -lightcolor $colors(-border) \
            -troughcolor $colors(-darker) \
            -focuscolor $colors(-primary) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -selectborderwidth 0 \
            -insertwidth 1 \
            -insertcolor $colors(-primary) \
            -relief flat

        # Frame
        ttk::style configure TFrame \
            -background $colors(-bg) \
            -borderwidth 0 \
            -relief flat

        ttk::style configure Card.TFrame \
            -background $colors(-dark) \
            -borderwidth 2 \
            -relief groove \
            -bordercolor $colors(-border-light)

        # Label - Extended dynamic typography system
        ttk::style configure TLabel \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -font {{Segoe UI} 10 bold} \
            -padding {8 6}

        ttk::style configure Display.TLabel \
            -font {{Segoe UI} 28 bold} \
            -foreground $colors(-primary) \
            -padding {0 0}

        ttk::style configure LargeTitle.TLabel \
            -font {{Segoe UI} 24 bold} \
            -foreground $colors(-fg) \
            -padding {0 0}

        ttk::style configure Title.TLabel \
            -font {{Segoe UI} 24 bold} \
            -foreground $colors(-fg) \
            -padding {0 0}

        ttk::style configure Headline.TLabel \
            -font {{Segoe UI} 16 bold} \
            -foreground $colors(-primary) \
            -padding {0 0}

        ttk::style configure Subtitle.TLabel \
            -font {{Segoe UI} 14 bold} \
            -foreground $colors(-fg) \
            -padding {0 0}

        ttk::style configure Heading.TLabel \
                        -font {{Segoe UI} 12 bold} \
            -foreground $colors(-primary) \
            -padding {0 0}

                ttk::style configure Body.TLabel \
                        -font {{Segoe UI} 10} \
            -foreground $colors(-fg) \
            -padding {6 4}

        ttk::style configure Caption.TLabel \
            -font {{Segoe UI} 9} \
            -foreground $colors(-text-secondary) \
                        -padding {6 4}

        ttk::style configure Small.TLabel \
            -font {{Segoe UI} 8} \
                        -foreground $colors(-text-secondary) \
            -padding {4 2}

        ttk::style configure Success.TLabel \
                        -font {{Segoe UI} 10 bold} \
            -foreground $colors(-success)

        ttk::style configure Warning.TLabel \
                        -font {{Segoe UI} 10 bold} \
            -foreground $colors(-warning)

        ttk::style configure Error.TLabel \
                        -font {{Segoe UI} 10 bold} \
            -foreground $colors(-error)

        ttk::style configure Info.TLabel \
                        -font {{Segoe UI} 10 bold} \
            -foreground $colors(-info)

        # Button - soft rounded design
                ttk::style configure TButton \
                        -font {{Segoe UI} 10 bold} \
            -background $colors(-active-bg) \
            -foreground $colors(-fg) \
                        -bordercolor $colors(-border-light) \
            -lightcolor $colors(-hover-bg) \
            -darkcolor $colors(-border) \
            -borderwidth 2 \
                        -focuscolor "" \
            -padding {16 8} \
            -relief raised

        # Large Button variant
        ttk::style configure Large.TButton \
            -font {{Segoe UI} 12 bold} \
            -padding {20 12} \
            -borderwidth 2

        # Small Button variant
        ttk::style configure Small.TButton \
            -font {{Segoe UI} 8 bold} \
            -padding {12 6} \
            -borderwidth 2

        ttk::style map TButton \
            -background [list \
                active $colors(-primary-hover) \
                pressed $colors(-active-bg) \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                active $colors(-fg) \
                disabled $colors(-disabled-fg)] \
            -bordercolor [list \
                active $colors(-primary-hover) \
                disabled $colors(-border)] \
            -lightcolor [list \
                active $colors(-primary-hover) \
                pressed $colors(-active-bg)] \
            -darkcolor [list \
                active $colors(-primary-hover) \
                pressed $colors(-active-bg)] \
            -relief [list \
                pressed sunken]

        # Primary Button - accent color with soft rounded edges
        ttk::style configure Primary.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-primary) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-primary-light) \
            -lightcolor $colors(-primary-light) \
            -darkcolor $colors(-primary-hover) \
            -borderwidth 2 \
            -padding {16 8} \
            -relief raised

        ttk::style map Primary.TButton \
            -background [list \
                active $colors(-primary-hover) \
                pressed $colors(-primary-hover) \
                disabled $colors(-disabled-bg)] \
            -lightcolor [list \
                active $colors(-primary-light) \
                pressed $colors(-primary-hover)] \
            -darkcolor [list \
                active $colors(-primary-hover) \
                pressed $colors(-primary-hover)] \
            -relief [list \
                pressed sunken]

        # Secondary Button - soft rounded edges
        ttk::style configure Secondary.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-secondary) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-secondary) \
            -lightcolor $colors(-secondary) \
            -darkcolor $colors(-secondary-hover) \
            -borderwidth 2 \
            -padding {16 8} \
            -relief raised

        ttk::style map Secondary.TButton \
            -background [list \
                active $colors(-secondary-hover) \
                pressed $colors(-secondary-hover) \
                disabled $colors(-disabled-bg)] \
            -relief [list \
                pressed sunken]

        # Accent Button - lime green from app.css
        ttk::style configure Accent.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-tertiary) \
            -foreground "#000000" \
            -bordercolor $colors(-tertiary) \
            -lightcolor $colors(-tertiary) \
            -darkcolor "#9fad00" \
            -borderwidth 2 \
            -padding {16 8} \
            -relief raised

        ttk::style map Accent.TButton \
            -background [list \
                active "#9fad00" \
                pressed "#9fad00" \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)] \
            -relief [list \
                pressed sunken]

        # Success Button - green from app.css
        ttk::style configure Success.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-success) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-success) \
            -lightcolor $colors(-success) \
            -darkcolor "#1e9038" \
            -borderwidth 2 \
            -padding {16 8} \
            -relief raised

        ttk::style map Success.TButton \
            -background [list \
                active "#1e9038" \
                pressed "#1e9038" \
                disabled $colors(-disabled-bg)] \
            -relief [list \
                pressed sunken]

        # Link Button - blue link from app.css
        ttk::style configure Link.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-bg) \
            -foreground $colors(-info) \
            -borderwidth 0 \
            -padding {14 8} \
            -relief flat

        ttk::style map Link.TButton \
            -foreground [list \
                active $colors(-primary-light) \
                pressed $colors(-primary-hover) \
                disabled $colors(-disabled-fg)]

        # Outline Button - soft rounded with bold font
        ttk::style configure Outline.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-bg) \
            -foreground $colors(-primary) \
            -bordercolor $colors(-primary) \
            -lightcolor $colors(-hover-bg) \
            -darkcolor $colors(-border) \
            -borderwidth 2 \
            -padding {16 8} \
            -relief raised

        ttk::style map Outline.TButton \
            -background [list \
                active $colors(-hover-bg) \
                pressed $colors(-active-bg)] \
            -bordercolor [list \
                active $colors(-primary-light) \
                disabled $colors(-border)] \
            -relief [list \
                pressed sunken]

        # Text Button - bold font with padding
        ttk::style configure Text.TButton \
            -font {{Segoe UI} 10 bold} \
            -background $colors(-bg) \
            -foreground $colors(-primary) \
            -borderwidth 0 \
            -padding {14 8}

        ttk::style map Text.TButton \
            -background [list \
                active $colors(-hover-bg) \
                pressed $colors(-active-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)]

        # Entry - soft rounded design with subtle depth
        ttk::style configure TEntry \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-inputfg) \
            -bordercolor $colors(-border-light) \
            -lightcolor $colors(-border) \
            -darkcolor $colors(-hover-bg) \
            -insertcolor $colors(-fg) \
            -padding {10 8} \
            -borderwidth 2 \
            -relief sunken

        ttk::style map TEntry \
            -fieldbackground [list \
                readonly $colors(-disabled-bg) \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)] \
            -bordercolor [list \
                focus $colors(-primary) \
                invalid $colors(-error)]

        # Combobox - soft rounded design
        ttk::style configure TCombobox \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-inputfg) \
            -background $colors(-bg) \
            -bordercolor $colors(-border-light) \
            -arrowcolor $colors(-fg) \
            -padding {10 8} \
            -borderwidth 2 \
            -relief sunken

        ttk::style map TCombobox \
            -fieldbackground [list \
                readonly $colors(-inputbg) \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)] \
            -bordercolor [list \
                focus $colors(-primary)] \
            -arrowcolor [list \
                disabled $colors(-disabled-fg)]

        # Checkbutton - bold font
        ttk::style configure TCheckbutton \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -font {{Segoe UI} 10 bold} \
            -padding {10 6} \
            -indicatorcolor $colors(-inputbg) \
            -indicatorbackground $colors(-inputbg) \
            -indicatormargin {0 0 10 0} \
            -borderwidth 0 \
            -relief flat

        ttk::style map TCheckbutton \
            -background [list \
                active $colors(-bg) \
                selected $colors(-bg)] \
            -foreground [list \
                active $colors(-primary) \
                disabled $colors(-disabled-fg)] \
            -indicatorcolor [list \
                selected $colors(-primary) \
                active $colors(-hover-bg) \
                disabled $colors(-disabled-bg)]

        # Radiobutton - sleek hover effect with bold font
        ttk::style configure TRadiobutton \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -font {{Segoe UI} 10 bold} \
            -padding {10 6} \
            -indicatorcolor $colors(-inputbg) \
            -indicatorbackground $colors(-inputbg) \
            -indicatormargin {0 0 10 0} \
            -borderwidth 0 \
            -relief flat

        ttk::style map TRadiobutton \
            -background [list \
                active $colors(-bg) \
                selected $colors(-bg)] \
            -foreground [list \
                active $colors(-primary) \
                selected $colors(-primary) \
                disabled $colors(-disabled-fg)] \
            -indicatorcolor [list \
                selected $colors(-primary) \
                active $colors(-hover-bg) \
                disabled $colors(-disabled-bg)]

        # Scrollbar - minimal sleek design without arrows
        ttk::style configure TScrollbar \
            -background $colors(-border) \
            -bordercolor $colors(-bg) \
            -troughcolor $colors(-bg) \
            -arrowsize 0 \
            -borderwidth 0 \
            -relief flat \
            -width 10

        ttk::style map TScrollbar \
            -background [list \
                active $colors(-primary) \
                pressed $colors(-primary-hover)]

        ttk::style configure Vertical.TScrollbar \
            -background $colors(-border) \
            -bordercolor $colors(-bg) \
            -troughcolor $colors(-bg) \
            -arrowsize 0 \
            -borderwidth 0 \
            -width 10

        ttk::style map Vertical.TScrollbar \
            -background [list \
                active $colors(-primary) \
                pressed $colors(-primary-hover)]

        ttk::style configure Horizontal.TScrollbar \
            -background $colors(-border) \
            -bordercolor $colors(-bg) \
            -troughcolor $colors(-bg) \
            -arrowsize 0 \
            -borderwidth 0 \
            -width 10

        ttk::style map Horizontal.TScrollbar \
            -background [list \
                active $colors(-primary) \
                pressed $colors(-primary-hover)]

        # Scale - clearer track and larger thumb
        ttk::style configure TScale \
            -background $colors(-primary) \
            -troughcolor $colors(-border) \
            -bordercolor $colors(-border-light) \
            -slidercolor $colors(-primary) \
            -borderwidth 1 \
            -sliderrelief raised \
            -sliderlength 20

        ttk::style map TScale \
            -background [list \
                active $colors(-primary-light) \
                pressed $colors(-primary-hover)] \
            -slidercolor [list \
                active $colors(-primary-light) \
                pressed $colors(-primary-hover)]

        # Colour picker scale variant - stronger contrast and larger grab handle
        ttk::style configure ColourPicker.Horizontal.TScale \
            -background $colors(-primary) \
            -troughcolor $colors(-darker) \
            -bordercolor $colors(-border-light) \
            -slidercolor $colors(-primary-light) \
            -borderwidth 1 \
            -sliderrelief raised \
            -sliderlength 24

        ttk::style map ColourPicker.Horizontal.TScale \
            -background [list \
                active $colors(-primary-light) \
                pressed $colors(-primary-hover)] \
            -slidercolor [list \
                active $colors(-primary) \
                pressed $colors(-primary-hover)]

        # Progressbar - soft rounded design
        ttk::style configure TProgressbar \
            -background $colors(-primary) \
            -troughcolor $colors(-darker) \
            -bordercolor $colors(-border-light) \
            -lightcolor $colors(-primary-light) \
            -darkcolor $colors(-primary-hover) \
            -borderwidth 2 \
            -thickness 24 \
            -relief raised

        # Notebook - soft rounded tabs
        ttk::style configure TNotebook \
            -background $colors(-bg) \
            -bordercolor $colors(-border-light) \
            -tabmargins {2 5 2 0} \
            -borderwidth 2

        ttk::style configure TNotebook.Tab \
            -background $colors(-dark) \
            -foreground $colors(-text-secondary) \
            -bordercolor $colors(-border-light) \
            -font {{Segoe UI} 11 bold} \
            -padding {18 10} \
            -borderwidth 2

        ttk::style map TNotebook.Tab \
            -background [list \
                selected $colors(-bg) \
                active $colors(-hover-bg)] \
            -foreground [list \
                selected $colors(-primary) \
                active $colors(-fg)] \
            -expand [list \
                selected {2 2 2 0}]

        # Treeview - soft design with bold headings
        ttk::style configure Treeview \
            -background $colors(-inputbg) \
            -foreground $colors(-fg) \
            -fieldbackground $colors(-inputbg) \
            -bordercolor $colors(-border-light) \
            -lightcolor $colors(-border-light) \
            -darkcolor $colors(-border) \
            -borderwidth 2 \
            -rowheight 32 \
            -padding {6 4}

        ttk::style map Treeview \
            -background [list selected $colors(-primary)] \
            -foreground [list selected $colors(-selectfg)]

        ttk::style configure Treeview.Heading \
            -background $colors(-dark) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-border-light) \
            -relief raised \
            -padding {10 8} \
            -font {{Segoe UI} 11 bold}

        ttk::style map Treeview.Heading \
            -background [list active $colors(-hover-bg)] \
            -relief [list pressed sunken]

        # Separator
        ttk::style configure TSeparator \
            -background $colors(-border)

        ttk::style configure Horizontal.TSeparator \
            -background $colors(-border)

        ttk::style configure Vertical.TSeparator \
            -background $colors(-border)

        # Labelframe - soft rounded design with depth
        ttk::style configure TLabelframe \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-border-light) \
            -lightcolor $colors(-hover-bg) \
            -darkcolor $colors(-border) \
            -borderwidth 2 \
            -relief groove \
            -padding {16 12}

        ttk::style configure TLabelframe.Label \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -font {{Segoe UI} 12 bold} \
            -padding {10 -8}

        # Panedwindow
        ttk::style configure TPanedwindow \
            -background $colors(-bg)

        ttk::style configure Sash \
            -sashthickness 8 \
            -gripcount 0 \
            -background $colors(-border)

        # Sizegrip
        ttk::style configure TSizegrip \
            -background $colors(-bg)

        # Spinbox - soft rounded design
        ttk::style configure TSpinbox \
            -fieldbackground $colors(-inputbg) \
            -foreground $colors(-inputfg) \
            -bordercolor $colors(-border-light) \
            -arrowcolor $colors(-fg) \
            -padding {10 8} \
            -borderwidth 2 \
            -relief sunken

        ttk::style map TSpinbox \
            -fieldbackground [list \
                readonly $colors(-disabled-bg) \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)] \
            -bordercolor [list \
                focus $colors(-primary)]

        # Menubutton - soft rounded design
        ttk::style configure TMenubutton \
            -background $colors(-dark) \
            -foreground $colors(-fg) \
            -bordercolor $colors(-border-light) \
            -arrowcolor $colors(-fg) \
            -padding {14 8} \
            -borderwidth 2 \
            -relief raised

        ttk::style map TMenubutton \
            -background [list \
                active $colors(-hover-bg) \
                pressed $colors(-active-bg) \
                disabled $colors(-disabled-bg)] \
            -foreground [list \
                disabled $colors(-disabled-fg)] \
            -relief [list \
                pressed sunken]
    }
}

# ============================================================================
# LIGHT MODE THEME
# ============================================================================

# Set default options for tk widgets (non-ttk)
option add *Background "#1e1e1e"
option add *Foreground "#ffffff"
option add *Font {{Segoe UI} 10 bold}
option add *selectBackground "#1b6ec2"
option add *selectForeground "#ffffff"
option add *activeBackground "#2a2d2e"
option add *activeForeground "#ffffff"
option add *highlightColor "#1b6ec2"
option add *highlightBackground "#1e1e1e"
option add *disabledForeground "#666666"
option add *insertBackground "#ffffff"
option add *troughColor "#2d2d2d"
option add *borderWidth 1
option add *relief flat

# Listbox specific - matches design theme
option add *Listbox.background "#2d2d2d"
option add *Listbox.foreground "#ffffff"
option add *Listbox.selectBackground "#1b6ec2"
option add *Listbox.selectForeground "#ffffff"
option add *Listbox.font {{Segoe UI} 10}
option add *Listbox.borderWidth 1
option add *Listbox.relief flat
option add *Listbox.highlightThickness 1
option add *Listbox.highlightColor "#3d3d3d"
option add *Listbox.highlightBackground "#3d3d3d"

# Text widget specific
option add *Text.background "#2d2d2d"
option add *Text.foreground "#ffffff"
option add *Text.insertBackground "#ffffff"
option add *Text.selectBackground "#1b6ec2"
option add *Text.selectForeground "#ffffff"
option add *Text.font {{Segoe UI} 10}
option add *Text.borderWidth 1
option add *Text.relief flat
option add *Text.highlightThickness 1
option add *Text.highlightColor "#1b6ec2"

# Canvas specific
option add *Canvas.background "#1e1e1e"
option add *Canvas.highlightThickness 0

# Menu specific
option add *Menu.background "#2d2d2d"
option add *Menu.foreground "#ffffff"
option add *Menu.activeBackground "#1b6ec2"
option add *Menu.activeForeground "#ffffff"
option add *Menu.activeBorderWidth 0
option add *Menu.borderWidth 1
option add *Menu.relief flat
option add *Menu.font {{Segoe UI} 10}

# Toplevel/window specific
option add *Toplevel.background "#1e1e1e"

# Message widget
option add *Message.background "#1e1e1e"
option add *Message.foreground "#ffffff"
option add *Message.font {{Segoe UI} 10}
