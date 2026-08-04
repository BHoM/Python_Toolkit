import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw
# --- Color Math Helpers ---
def hex_to_rgb(hex_color):
   """Convert a hex color string to an RGB tuple (0-255)."""
   hex_color = hex_color.lstrip('#')
   return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def rgb_to_hex(rgb):
   """Convert an RGB tuple to a hex color string."""
   return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"
def interpolate(c1, c2, t):
   """Linearly interpolate between two RGB tuples based on a factor t (0.0 to 1.0)."""
   return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(3))
def get_color_at(t, sorted_stops):
   """Returns the interpolated RGB color for a given position t (0.0 to 1.0)."""
   if t <= sorted_stops[0]['pos'].get():
       return hex_to_rgb(sorted_stops[0]['color'])
   if t >= sorted_stops[-1]['pos'].get():
       return hex_to_rgb(sorted_stops[-1]['color'])
   for i in range(len(sorted_stops) - 1):
       s1 = sorted_stops[i]
       s2 = sorted_stops[i+1]
       p1, p2 = s1['pos'].get(), s2['pos'].get()
       if p1 <= t <= p2:
           span = p2 - p1
           local_t = 0 if span == 0 else (t - p1) / span
           rgb1 = hex_to_rgb(s1['color'])
           rgb2 = hex_to_rgb(s2['color'])
           return interpolate(rgb1, rgb2, local_t)
   return (0, 0, 0)
# --- Main Application ---
class GradientDesigner(tk.Tk):
   def __init__(self):
       super().__init__()
       self.title("Advanced Gradient Designer")
       self.geometry("650x800")
       self.configure(padx=20, pady=20)
       self.swatches_var = tk.IntVar(value=256)
       self.swatches_var.trace_add("write", lambda *args: self.render_gradient())
       # Initialize stops using our new helper method
       self.stops = [
           self._create_stop("#4c71ff", 0.0),
           self._create_stop("#0025b3", 0.25),
           self._create_stop("#000000", 0.50),
           self._create_stop("#c7030d", 0.75),
           self._create_stop("#fc4a53", 1.0),
       ]
       self.setup_ui()
       self.render_gradient()
   def _create_stop(self, color, pos_val):
       """Helper to create a stop dictionary with a traced DoubleVar."""
       var = tk.DoubleVar(value=pos_val)
       var.trace_add("write", lambda *args: self.render_gradient())
       return {"color": color, "pos": var}
   def setup_ui(self):
       # 1. Canvas & Swatches Control
       header_frame = tk.Frame(self)
       header_frame.pack(fill="x", pady=(0, 5))
       tk.Label(header_frame, text="Gradient Preview", font=("Arial", 12, "bold")).pack(side="left")
       tk.Entry(header_frame, textvariable=self.swatches_var, width=5).pack(side="right")
       tk.Label(header_frame, text="Swatches:").pack(side="right", padx=5)
       self.canvas_width = 600
       self.canvas_height = 100
       self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bd=2, relief="sunken")
       self.canvas.pack(pady=(0, 10))
       # 2. Tool Buttons (Distribute, Reverse, Mirror)
       tools_frame = tk.Frame(self)
       tools_frame.pack(fill="x", pady=(0, 10))
       tk.Button(tools_frame, text="↔ Distribute Evenly", command=self.distribute_evenly).pack(side="left", padx=(0, 5))
       tk.Button(tools_frame, text="🔁 Reverse", command=self.reverse_gradient).pack(side="left", padx=5)
       tk.Button(tools_frame, text="🪞 Mirror", command=self.mirror_gradient).pack(side="left", padx=5)
       tk.Button(tools_frame, text="➕ Add Node", command=self.add_stop).pack(side="right")
       # 3. Controls Area
       tk.Label(self, text="Adjust Color Nodes", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
       # --- Scrollable Container Setup ---
       container = tk.Frame(self)
       container.pack(fill="both", expand=True, pady=5)
       self.canvas_scroll = tk.Canvas(container, highlightthickness=0)
       scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas_scroll.yview)
       self.controls_frame = tk.Frame(self.canvas_scroll)
       self.canvas_scroll.configure(yscrollcommand=scrollbar.set)
       scrollbar.pack(side="right", fill="y")
       self.canvas_scroll.pack(side="left", fill="both", expand=True)
       # Place the frame inside the canvas
       self.canvas_window = self.canvas_scroll.create_window((0, 0), window=self.controls_frame, anchor="nw")
       # Update scroll region when the internal frame resizes (e.g., adding/removing nodes)
       self.controls_frame.bind(
           "<Configure>",
           lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
       )
       # Keep the internal frame width synced with the canvas width
       self.canvas_scroll.bind(
           "<Configure>",
           lambda e: self.canvas_scroll.itemconfig(self.canvas_window, width=e.width)
       )
       # Mouse wheel bindings (Covers Windows, macOS, and Linux)
       self.bind_all("<MouseWheel>", lambda e: self.canvas_scroll.yview_scroll(int(-1*(e.delta/120)), "units"))
       self.bind_all("<Button-4>", lambda e: self.canvas_scroll.yview_scroll(-1, "units"))
       self.bind_all("<Button-5>", lambda e: self.canvas_scroll.yview_scroll(1, "units"))
       # ----------------------------------
       self.build_control_rows()
       # 4. Image Export Area
       tk.Label(self, text="Export", font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
       tk.Button(self, text="💾 Export as PNG Image", bg="#4c71ff", fg="white",
                 font=("Arial", 10, "bold"), command=self.export_image).pack(anchor="w")
   def build_control_rows(self):
       for widget in self.controls_frame.winfo_children():
           widget.destroy()
       for i, stop in enumerate(self.stops):
           row = tk.Frame(self.controls_frame)
           row.pack(fill="x", pady=4)
           btn = tk.Button(row, bg=stop["color"], width=5, command=lambda idx=i: self.choose_color(idx))
           btn.pack(side="left", padx=5)
           scale = tk.Scale(row, from_=0.0, to=1.0, resolution=0.001, orient="horizontal",
                            length=350, showvalue=False, variable=stop["pos"])
           scale.pack(side="left", padx=10)
           entry = tk.Entry(row, textvariable=stop["pos"], width=6)
           entry.pack(side="left", padx=5)
           if len(self.stops) > 2:
               del_btn = tk.Button(row, text="❌", command=lambda idx=i: self.remove_stop(idx))
               del_btn.pack(side="left")
   # --- Tool Actions ---
   def distribute_evenly(self):
       if len(self.stops) < 2: return
       # Sort visually first so colors stay in their current order
       self.stops.sort(key=lambda s: s['pos'].get())
       n = len(self.stops)
       for i, stop in enumerate(self.stops):
           stop['pos'].set(i / (n - 1))
       self.build_control_rows()
   def reverse_gradient(self):
       # Invert all positions (1.0 becomes 0.0, 0.25 becomes 0.75)
       for stop in self.stops:
           stop['pos'].set(1.0 - stop['pos'].get())
       # Re-sort to keep UI rows cleanly ordered from 0.0 to 1.0
       self.stops.sort(key=lambda s: s['pos'].get())
       self.build_control_rows()
   def mirror_gradient(self):
       # Save current layout strictly ordered
       original = sorted([(s['color'], s['pos'].get()) for s in self.stops], key=lambda x: x[1])
       # Clear current stops
       self.stops.clear()
       # 1. Compress the original gradient into the first half (0.0 to 0.5)
       for color, p in original:
           self.stops.append(self._create_stop(color, p / 2.0))
       # 2. Append the reversed gradient into the second half (0.5 to 1.0)
       # We skip the very last original node ([:-1]) so we don't put two identical nodes at exactly 0.5
       for color, p in reversed(original[:-1]):
           self.stops.append(self._create_stop(color, 1.0 - (p / 2.0)))
       self.build_control_rows()
       self.render_gradient()
   # --- Standard Actions ---
   def choose_color(self, idx):
       current_color = self.stops[idx]["color"]
       _, hex_color = colorchooser.askcolor(initialcolor=current_color, title="Select Color")
       if hex_color:
           self.stops[idx]["color"] = hex_color
           self.build_control_rows()
           self.render_gradient()
   def add_stop(self):
       self.stops.append(self._create_stop("#ffffff", 1.0))
       self.build_control_rows()
       self.render_gradient()
   def remove_stop(self, idx):
       if len(self.stops) > 2:
           self.stops.pop(idx)
           self.build_control_rows()
           self.render_gradient()
   def render_gradient(self):
       try:
           num_swatches = self.swatches_var.get()
           if num_swatches < 1: return
       except tk.TclError:
           return
       self.canvas.delete("gradient")
       sorted_stops = sorted(self.stops, key=lambda s: s['pos'].get())
       for x in range(self.canvas_width):
           swatch_index = int((x / self.canvas_width) * num_swatches)
           t = swatch_index / (num_swatches - 1) if num_swatches > 1 else 0.5
           rgb = get_color_at(t, sorted_stops)
           hex_col = rgb_to_hex(rgb)
           self.canvas.create_line(x, 0, x, self.canvas_height, fill=hex_col, tags="gradient")
   def export_image(self):
       try:
           num_swatches = self.swatches_var.get()
       except tk.TclError:
           num_swatches = 256
       file_path = filedialog.asksaveasfilename(
           defaultextension=".png",
           filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
           title="Save Gradient Image"
       )
       if not file_path: return
       img_width, img_height = 1024, 256
       image = Image.new("RGB", (img_width, img_height))
       draw = ImageDraw.Draw(image)
       sorted_stops = sorted(self.stops, key=lambda s: s['pos'].get())
       for x in range(img_width):
           swatch_index = int((x / img_width) * num_swatches)
           t = swatch_index / (num_swatches - 1) if num_swatches > 1 else 0.5
           rgb = get_color_at(t, sorted_stops)
           draw.line([(x, 0), (x, img_height)], fill=tuple(int(c) for c in rgb))
       try:
           image.save(file_path)
           messagebox.showinfo("Success", f"Gradient exported successfully to:\n{file_path}")
       except Exception as e:
           messagebox.showerror("Export Error", f"Failed to save image:\n{e}")
if __name__ == "__main__":
   app = GradientDesigner()
   app.mainloop()

   
   