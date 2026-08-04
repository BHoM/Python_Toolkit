import tkinter as tk
from tkinter import colorchooser
# --- Color Math Helpers ---
def hex_to_rgb(hex_color):
   """Convert a hex color string to an RGB tuple."""
   hex_color = hex_color.lstrip('#')
   return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def rgb_to_hex(rgb):
   """Convert an RGB tuple to a hex color string."""
   return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
def interpolate(c1, c2, t):
   """Linearly interpolate between two RGB tuples based on a factor t (0.0 to 1.0)."""
   return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))
# --- Main Application ---
class GradientDesigner(tk.Tk):
   def __init__(self):
       super().__init__()
       self.title("Tkinter Gradient Designer")
       self.geometry("600x700")
       self.configure(padx=20, pady=20)
       # Initial colors based on your URL
       self.stops = [
           {"color": "#4c71ff", "pos": 0.0},
           {"color": "#0025b3", "pos": 0.25},
           {"color": "#000000", "pos": 0.50},
           {"color": "#c7030d", "pos": 0.75},
           {"color": "#fc4a53", "pos": 1.0},
       ]
       self.setup_ui()
       self.render_gradient()
       self.update_export_code()
   def setup_ui(self):
       # 1. Canvas for Preview
       tk.Label(self, text="Gradient Preview", font=("Arial", 12, "bold")).pack(anchor="w")
       self.canvas_width = 560
       self.canvas_height = 100
       self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bd=2, relief="sunken")
       self.canvas.pack(pady=(5, 20))
       # 2. Controls Area
       tk.Label(self, text="Adjust Color Nodes", font=("Arial", 12, "bold")).pack(anchor="w")
       # Frame to hold dynamic rows of sliders/buttons
       self.controls_frame = tk.Frame(self)
       self.controls_frame.pack(fill="x", pady=5)
       self.build_control_rows()
       # 3. Add Node Button
       tk.Button(self, text="➕ Add Color Node", command=self.add_stop).pack(pady=10)
       # 4. Code Export Area
       tk.Label(self, text="CSS Export", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
       self.export_text = tk.Text(self, height=3, width=65, bg="#f0f0f0")
       self.export_text.pack()
   def build_control_rows(self):
       # Clear existing controls
       for widget in self.controls_frame.winfo_children():
           widget.destroy()
       # Create a row for each stop
       for i, stop in enumerate(self.stops):
           row = tk.Frame(self.controls_frame)
           row.pack(fill="x", pady=2)
           # Color Chooser Button
           btn = tk.Button(row, bg=stop["color"], width=5,
                           command=lambda idx=i: self.choose_color(idx))
           btn.pack(side="left", padx=5)
           # Position Slider
           scale = tk.Scale(row, from_=0.0, to=1.0, resolution=0.01, orient="horizontal",
                            length=350, showvalue=True,
                            command=lambda val, idx=i: self.update_pos(idx, val))
           scale.set(stop["pos"])
           scale.pack(side="left", padx=10)
           # Delete Button
           if len(self.stops) > 2:
               del_btn = tk.Button(row, text="❌", command=lambda idx=i: self.remove_stop(idx))
               del_btn.pack(side="left")
   def choose_color(self, idx):
       current_color = self.stops[idx]["color"]
       # Open Tkinter's native color picker
       _, hex_color = colorchooser.askcolor(initialcolor=current_color, title="Select Color")
       if hex_color:
           self.stops[idx]["color"] = hex_color
           self.build_control_rows()
           self.render_gradient()
           self.update_export_code()
   def update_pos(self, idx, val):
       self.stops[idx]["pos"] = float(val)
       self.render_gradient()
       self.update_export_code()
   def add_stop(self):
       # Add a new stop at the end
       self.stops.append({"color": "#ffffff", "pos": 1.0})
       self.build_control_rows()
       self.render_gradient()
       self.update_export_code()
   def remove_stop(self, idx):
       if len(self.stops) > 2:
           self.stops.pop(idx)
           self.build_control_rows()
           self.render_gradient()
           self.update_export_code()
   def render_gradient(self):
       self.canvas.delete("gradient")
       # Sort stops strictly by position for rendering
       sorted_stops = sorted(self.stops, key=lambda s: s['pos'])
       # Draw the gradient line by line
       for x in range(self.canvas_width):
           t = x / self.canvas_width  # Global position from 0.0 to 1.0
           # Handle edge cases (before first stop or after last stop)
           if t <= sorted_stops[0]['pos']:
               color = sorted_stops[0]['color']
           elif t >= sorted_stops[-1]['pos']:
               color = sorted_stops[-1]['color']
           else:
               # Find which two stops this pixel falls between
               for i in range(len(sorted_stops) - 1):
                   s1 = sorted_stops[i]
                   s2 = sorted_stops[i+1]
                   if s1['pos'] <= t <= s2['pos']:
                       span = s2['pos'] - s1['pos']
                       if span == 0:  # Prevent division by zero if sliders overlap
                           local_t = 0
                       else:
                           local_t = (t - s1['pos']) / span
                       rgb1 = hex_to_rgb(s1['color'])
                       rgb2 = hex_to_rgb(s2['color'])
                       interp_rgb = interpolate(rgb1, rgb2, local_t)
                       color = rgb_to_hex(interp_rgb)
                       break
           # Draw a 1-pixel wide vertical line on the canvas
           self.canvas.create_line(x, 0, x, self.canvas_height, fill=color, tags="gradient")
   def update_export_code(self):
       sorted_stops = sorted(self.stops, key=lambda s: s['pos'])
       css_stops = ", ".join([f"{s['color']} {s['pos']*100:.1f}%" for s in sorted_stops])
       css_code = f"background: linear-gradient(90deg, {css_stops});"
       self.export_text.delete(1.0, tk.END)
       self.export_text.insert(tk.END, css_code)
if __name__ == "__main__":
   app = GradientDesigner()
   app.mainloop()