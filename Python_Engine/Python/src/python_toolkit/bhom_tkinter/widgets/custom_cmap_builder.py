import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Literal

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Colormap, to_rgba

from python_toolkit.bhom_tkinter.widgets import (
	Button, ColourPicker, Spinbox, FigureContainer, RadioSelection, PackingOptions,
)
from python_toolkit.bhom_tkinter import BHoMBasePopup, BHoMBaseWidget
from python_toolkit.bhom_tkinter.widgets.slider import Slider
from python_toolkit.plot.cmap_sample import cmap_sample_plot
from python_toolkit.bhom.custom_cmaps import save_custom_cmap, delete_custom_cmap, clear_custom_cmaps, list_custom_cmap_names
from python_toolkit.bhom.analytics import CONSOLE_LOGGER

_DEFAULT_COLOURS = [
	"#FF0000", "#FFD000", "#09FF00", "#00A2FF",
	"#9400FF", "#FF69B4", "#00FFFF", "#FF8C00",
]


class CmapBuilder(BHoMBaseWidget):
	"""A cmap builder popup. Builds and previews custom linear or binned colormaps."""

	def __init__(
		self,
		parent: ttk.Frame,
		no_colours: int = 4,
		command: Optional[Callable[[Colormap, tuple], None]] = None,
		**kwargs,
	) -> None:
		"""
		Args:
			parent: Parent widget.
			no_colours: Initial number of colour stops (minimum 2).
			command: Callback invoked with the built Colormap when Apply is pressed.
			**kwargs: Additional Frame options.
		"""
		super().__init__(parent, **kwargs)

		self.command = command
		self._cmap_builder_window: Optional[BHoMBasePopup] = None
		self.no_colours = max(2, int(no_colours))
		self._last_cmap: Optional[Colormap] = None
		self._last_bounds: tuple[float, float] = (0.0, 1.0)
		self._colour_rows: list[dict] = []

		self.builder_button = Button(
			self.content_frame,
			text="Add new Colour Collection",
			command=self._open_builder,
		)
		self.builder_button.pack(side="top", fill="x")

	# ------------------------------------------------------------------
	# Validators
	# ------------------------------------------------------------------

	def _validate_name(self, value: str) -> tuple[bool, str]:
		if not value.strip():
			return False, "Name cannot be empty."
		invalid_chars = set(r'\/:*?"<>|')
		if any(c in invalid_chars for c in value):
			return False, "Name contains invalid characters."
		# Block clashes with matplotlib's registered colormaps.
		if value in matplotlib.colormaps:
			return False, f"'{value}' is already a matplotlib colormap name."
		# Block duplicate saved names.
		if value in list_custom_cmap_names():
			return False, f"'{value}' already exists in saved collections. Delete it first."
		return True, ""

	# ------------------------------------------------------------------
	# Manager popup
	# ------------------------------------------------------------------

	def _open_manager(self) -> None:
		"""Open the saved-colourmap manager popup."""
		self._manager_window = BHoMBasePopup(
			self,
			title="Manage Saved Colour Collections",
			resizable=True,
		)
		self._build_manager_contents()
		self._manager_window.show()

	def _build_manager_contents(self) -> None:
		"""Populate (or repopulate) the manager popup body."""
		container = self._manager_window.content_frame
		for widget in container.winfo_children():
			widget.destroy()

		names = list_custom_cmap_names()

		if not names:
			ttk.Label(container, text="No saved colour collections found.").pack(
				padx=12, pady=12
			)
		else:
			# Scrollable list — canvas has a fixed height with NO expand=True so it
			# cannot grow to match its content (which would kill scrolling).
			list_frame = ttk.LabelFrame(container, text="Saved Collections", padding=6)
			list_frame.pack(side="top", fill="x", pady=(0, 8))

			ROW_H = 34
			canvas_h = min(len(names), 8) * ROW_H
			canvas = tk.Canvas(list_frame, highlightthickness=0, height=canvas_h)
			scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
			canvas.configure(yscrollcommand=scrollbar.set)
			scrollbar.pack(side="right", fill="y")
			canvas.pack(side="left", fill="x")  # fill="x" only — height stays fixed

			inner = ttk.Frame(canvas)
			win = canvas.create_window((0, 0), window=inner, anchor="nw")
			inner.bind(
				"<Configure>",
				lambda e: canvas.configure(scrollregion=(0, 0, e.width, e.height)),
			)
			canvas.bind(
				"<Configure>",
				lambda e: canvas.itemconfigure(win, width=e.width),
			)
			canvas.bind(
				"<MouseWheel>",
				lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"),
			)

			for name in names:
				row = ttk.Frame(inner)
				row.pack(fill="x", pady=2)
				ttk.Label(row, text=name).pack(side="left", padx=(4, 0))
				Button(
					row,
					text="Delete",
					command=lambda n=name: self._delete_saved(n),
				).pack(side="right", padx=(0, 4))

		# Bottom buttons
		btn_frame = ttk.Frame(container)
		btn_frame.pack(side="bottom", fill="x", pady=(4, 0))
		Button(
			btn_frame, text="Close", command=self._manager_window.close
		).pack(side="right", padx=(4, 0))
		if names:
			Button(
				btn_frame, text="Clear All", command=self._clear_all_saved
			).pack(side="right")

	def _delete_saved(self, name: str) -> None:
		"""Delete a single saved cmap and refresh the manager list."""
		delete_custom_cmap(name)
		self._build_manager_contents()

	def _clear_all_saved(self) -> None:
		"""Clear all saved cmaps and refresh the manager list."""
		clear_custom_cmaps()
		self._build_manager_contents()

	# ------------------------------------------------------------------
	# Builder popup
	# ------------------------------------------------------------------

	def _open_builder(self) -> None:
		"""Open the cmap builder popup."""
		if self._cmap_builder_window is not None and self._cmap_builder_window.winfo_exists():
			self._cmap_builder_window.focus_force()
			return

		self._cmap_builder_window = BHoMBasePopup(
			self,
			title="Colour Collection Builder",
			on_close=self._close_builder,
			resizable=True,
		)
		container = self._cmap_builder_window.content_frame

		# --- Settings ------------------------------------------------
		settings_frame = ttk.LabelFrame(container, text="Settings", padding=6)
		settings_frame.pack(side="top", fill="x", pady=(0, 8))

		name_row = ttk.Frame(settings_frame)
		name_row.pack(fill="x", pady=2)
		ttk.Label(name_row, text="Name:").pack(side="left")
		self._name_var = tk.StringVar(value="MyColourCollection")
		self._name_entry_widget = ttk.Entry(name_row, textvariable=self._name_var)
		self._name_entry_widget.pack(side="left", fill="x", expand=True, padx=(8, 0))

		# Inline validation status shown below the name field.
		self._name_status_var = tk.StringVar(value="")
		self._name_status_label = ttk.Label(
			settings_frame, textvariable=self._name_status_var, foreground="red"
		)
		self._name_status_label.pack(fill="x", padx=(0, 0))
		self._name_var.trace_add("write", lambda *_: self._on_name_changed())

		colours_row = ttk.Frame(settings_frame)
		colours_row.pack(fill="x", pady=2)
		ttk.Label(colours_row, text="Colours:").pack(side="left")
		self._no_colours_spin = Spinbox(
			colours_row, from_=2, to=20, default=self.no_colours,
			command=self._on_no_colours_changed,
		)
		self._no_colours_spin.pack(side="left", padx=(8, 0))

		type_row = ttk.Frame(settings_frame)
		type_row.pack(fill="x", pady=2)
		ttk.Label(type_row, text="Type:").pack(side="left")
		self._type_radio = RadioSelection(
			type_row,
			fields=["Interpolation", "Bins"],
			default="Interpolation",
			command=self._on_type_changed,
			orient="horizontal",
		)
		self._type_radio.pack(side="left", padx=(8, 0))

		range_row = ttk.Frame(settings_frame)
		range_row.pack(fill="x", pady=2)
		ttk.Label(range_row, text="Range:").pack(side="left")
		self._vmin_var = tk.DoubleVar(value=0.0)
		self._vmax_var = tk.DoubleVar(value=1.0)
		vmin_entry = ttk.Entry(range_row, textvariable=self._vmin_var, width=8)
		vmin_entry.pack(side="left", padx=(8, 4))
		ttk.Label(range_row, text="to").pack(side="left")
		vmax_entry = ttk.Entry(range_row, textvariable=self._vmax_var, width=8)
		vmax_entry.pack(side="left", padx=(4, 0))
		for _entry in (vmin_entry, vmax_entry):
			_entry.bind("<FocusOut>", lambda _e: self._on_range_changed())
			_entry.bind("<Return>", lambda _e: self._on_range_changed())

		# --- Colour stops (scrollable) --------------------------------
		stops_frame = ttk.LabelFrame(container, text="Colour Stops", padding=6)
		stops_frame.pack(side="top", fill="x", pady=(0, 8))

		# Canvas uses fill="x" with NO expand so its height is always exactly
		# what we configure — it cannot grow to match content, which is what
		# makes the scrollbar usable.
		self._stops_canvas = tk.Canvas(stops_frame, highlightthickness=0, height=160)
		self._stops_scrollbar = ttk.Scrollbar(
			stops_frame, orient="vertical", command=self._stops_canvas.yview
		)
		self._stops_canvas.configure(yscrollcommand=self._stops_scrollbar.set)
		self._stops_scrollbar.pack(side="right", fill="y")
		self._stops_canvas.pack(side="left", fill="x", expand=True)  # expand claims full cavity width

		self._colour_rows_frame = ttk.Frame(self._stops_canvas)
		self._canvas_window = self._stops_canvas.create_window(
			(0, 0), window=self._colour_rows_frame, anchor="nw"
		)

		# e.height from <Configure> is the actual settled height — more reliable
		# than winfo_reqheight() called asynchronously.
		self._stops_content_h: int = 1
		def _on_rows_configure(e):
			self._stops_content_h = e.height
			self._stops_canvas.configure(scrollregion=(0, 0, e.width, e.height))
		self._colour_rows_frame.bind("<Configure>", _on_rows_configure)
		self._stops_canvas.bind(
			"<Configure>",
			lambda e: self._stops_canvas.itemconfigure(self._canvas_window, width=e.width),
		)
		self._stops_canvas.bind(
			"<MouseWheel>",
			lambda e: self._stops_canvas.yview_scroll(-1 * (e.delta // 120), "units"),
		)

		self._colour_rows = []
		self._build_colour_rows()

		# --- Preview -------------------------------------------------
		preview_frame = ttk.LabelFrame(container, text="Preview", padding=6)
		preview_frame.pack(side="top", fill="x", pady=(0, 8))
		self._preview_container = FigureContainer(
			preview_frame,
			rigid_width=400,
			rigid_height=50,
			build_options=PackingOptions(side="top", fill="x"),
		)
		self._preview_container.build()

		# --- Buttons -------------------------------------------------
		btn_frame = ttk.Frame(container)
		btn_frame.pack(side="bottom", fill="x", pady=(4, 0))
		Button(btn_frame, text="Cancel", command=self._cmap_builder_window.close).pack(
			side="right", padx=(4, 0)
		)
		Button(btn_frame, text="Add to Collection", command=self._apply_cmap, style="Primary.TButton").pack(side="right")
		Button(btn_frame, text="Manage Saved", command=self._open_manager).pack(side="left")

		self._update_cmap_preview()
		self._cmap_builder_window.show(focus_widget=self._name_entry_widget)

	def _build_colour_rows(self) -> None:
		"""Destroy and rebuild all colour stop rows from current state."""
		old_colours = [r["colour_picker"].get() for r in self._colour_rows]
		old_positions = [r["pos_var"].get() for r in self._colour_rows]

		for widget in self._colour_rows_frame.winfo_children():
			widget.destroy()
		self._colour_rows.clear()

		n = max(2, int(self._no_colours_spin.get()))
		is_interp = self._is_interpolation()
		vmin, vmax = self._get_range()
		resolution = max(1e-6, (vmax - vmin) / 100)

		for i in range(n):
			colour = (
				old_colours[i] if i < len(old_colours)
				else _DEFAULT_COLOURS[i % len(_DEFAULT_COLOURS)]
			)

			if is_interp:
				# First and last stops are locked to vmin / vmax
				if i == 0:
					pos, locked = vmin, True
				elif i == n - 1:
					pos, locked = vmax, True
				else:
					raw = float(old_positions[i]) if i < len(old_positions) else vmin + i * (vmax - vmin) / (n - 1)
					pos = max(vmin, min(vmax, raw))
					locked = False
			else:
				# Bins: pos_var stores the LOWER boundary (start) of each bin.
				# Bin i covers [lower_i, lower_{i+1}) where lower_{n} = vmax.
				# The first row is locked at vmin.
				if i == 0:
					pos, locked = vmin, True
				else:
					raw = float(old_positions[i]) if i < len(old_positions) else vmin + i * (vmax - vmin) / n
					pos = max(vmin, min(vmax, raw))
					locked = False

			row_frame = ttk.Frame(self._colour_rows_frame)
			row_frame.pack(fill="x", pady=1)

			picker = ColourPicker(
				row_frame,
				default_colour=colour,
				swatch_width=32,
				swatch_height=20,
				command=lambda _c: self._update_cmap_preview(),
			)
			picker.pack(side="left", padx=(0, 8))

			slider = Slider(
				row_frame,
				from_=vmin, to=vmax, default=pos,
				resolution=resolution,
				command=lambda _v: self._update_cmap_preview(),
			)
			slider.pack(side="left", fill="x", expand=True)
			if locked:
				slider.disable()
			pos_var = slider._var

			self._colour_rows.append({
				"frame": row_frame,
				"colour_picker": picker,
				"pos_var": pos_var,
				"slider": slider,
				"locked": locked,
			})

		# Bins: remind the user that the last bin always ends at vmax
		if not is_interp:
			ttk.Label(
				self._colour_rows_frame,
				text=f"  (Slider = start value of each bin; last bin ends at {vmax:.4g})",
				style="Caption.TLabel",
			).pack(anchor="w", pady=(2, 0))

		# Resize the viewport after the window is on screen.
		if hasattr(self, "_stops_canvas"):
			self._stops_canvas.after(10, self._fit_stops_canvas)

	def _on_name_changed(self) -> None:
		"""Real-time validation feedback as the user types a name."""
		if not hasattr(self, "_name_status_var"):
			return
		name = self._name_var.get().strip()
		valid, msg = self._validate_name(name)
		self._name_status_var.set("" if valid else msg)

	def _fit_stops_canvas(self) -> None:
		"""Resize the canvas height to show up to 4 rows; more activates the scrollbar."""
		if not hasattr(self, "_stops_canvas") or not hasattr(self, "_colour_rows_frame"):
			return
		n = len(self._colour_rows)
		content_h = getattr(self, "_stops_content_h", 0)
		if content_h <= 1:
			self._stops_canvas.after(20, self._fit_stops_canvas)
			return
		visible_h = content_h if n <= 4 else max(40, round(content_h * 4 / n))
		self._stops_canvas.configure(height=visible_h)
		self._stops_canvas.configure(
			scrollregion=(0, 0, self._colour_rows_frame.winfo_width(), content_h)
		)

	def _is_interpolation(self) -> bool:
		if not hasattr(self, "_type_radio"):
			return True
		return self._type_radio.get() == "Interpolation"

	def _get_range(self) -> tuple[float, float]:
		"""Return (vmin, vmax) from the range entries, guaranteed vmin < vmax."""
		try:
			vmin = float(self._vmin_var.get())
		except (ValueError, AttributeError, tk.TclError):
			vmin = 0.0
		try:
			vmax = float(self._vmax_var.get())
		except (ValueError, AttributeError, tk.TclError):
			vmax = 1.0
		if vmax <= vmin:
			vmax = vmin + 1.0
		return vmin, vmax

	# ------------------------------------------------------------------
	# Change handlers
	# ------------------------------------------------------------------

	def _on_no_colours_changed(self, _value) -> None:
		if not hasattr(self, "_colour_rows_frame"):
			return
		self._build_colour_rows()
		self._update_cmap_preview()

	def _on_type_changed(self, _value: str) -> None:
		if not hasattr(self, "_colour_rows_frame"):
			return
		self._build_colour_rows()
		self._update_cmap_preview()

	def _on_range_changed(self) -> None:
		if not hasattr(self, "_colour_rows_frame"):
			return
		self._build_colour_rows()
		self._update_cmap_preview()

	# ------------------------------------------------------------------
	# Colormap construction
	# ------------------------------------------------------------------

	def _build_current_cmap(self) -> Optional[Colormap]:
		"""Construct a Colormap from the current row state, always mapped to [0, 1]."""
		if not self._colour_rows:
			return None

		name = self._name_var.get().strip() if hasattr(self, "_name_var") else "custom"
		colours = [r["colour_picker"].get() for r in self._colour_rows]
		vmin, vmax = self._get_range()
		span = vmax - vmin

		def _norm(val: float) -> float:
			"""Normalise a user-unit value to [0, 1]."""
			return max(0.0, min(1.0, (val - vmin) / span))

		if self._is_interpolation():
			positions = [r["pos_var"].get() for r in self._colour_rows]
			positions[0] = vmin
			positions[-1] = vmax
			stops = sorted(
				((_norm(p), c) for p, c in zip(positions, colours)),
				key=lambda x: x[0],
			)
			return LinearSegmentedColormap.from_list(name, stops)
		else:
			# Bins: pos_var stores the LOWER boundary (start) of each bin.
			# Bin i covers [lower_i, lower_{i+1}) where lower_{n} = vmax.
			raw_starts = [r["pos_var"].get() for r in self._colour_rows]
			raw_starts[0] = vmin  # Enforce locked first boundary

			# Sort (lower_boundary, colour) pairs to guarantee monotonicity
			paired = sorted(zip(raw_starts, colours), key=lambda x: x[0])
			sorted_starts = [p[0] for p in paired]
			sorted_colours = [p[1] for p in paired]

			# Derive end boundaries: bin i ends where bin i+1 starts; last ends at vmax
			ends = sorted_starts[1:] + [vmax]
			norm_starts = [_norm(s) for s in sorted_starts]
			norm_ends_n = [_norm(e) for e in ends]
			norm_starts[0] = 0.0
			norm_ends_n[-1] = 1.0

			# Build piecewise-constant cmap: doubled boundary points create hard edges
			stops = []
			for i, colour in enumerate(sorted_colours):
				stops.append((norm_starts[i], colour))
				if i < len(sorted_colours) - 1:
					stops.append((norm_ends_n[i], colour))  # Hard edge at boundary
			stops.append((1.0, sorted_colours[-1]))
			return LinearSegmentedColormap.from_list(name, stops)

	def _update_cmap_preview(self) -> None:
		"""Regenerate the preview figure from the current row state."""
		if not hasattr(self, "_preview_container"):
			return
		try:
			cmap = self._build_current_cmap()
			if cmap is None:
				return
			vmin, vmax = self._get_range()
			fig = cmap_sample_plot(cmap, bounds=(vmin, vmax), figsize=(6, 0.5), bins=256)
			self._preview_container.embed_figure(fig)
			plt.close(fig)
		except Exception:
			pass

	def _apply_cmap(self) -> None:
		"""Validate, build the colormap, fire the command, and close the popup."""
		name = self._name_var.get().strip() if hasattr(self, "_name_var") else ""
		valid, msg = self._validate_name(name)
		if not valid:
			if hasattr(self, "_name_status_var"):
				self._name_status_var.set(msg)
			return

		cmap = self._build_current_cmap()
		if cmap is None:
			return

		vmin, vmax = self._get_range()
		self._last_cmap = cmap
		self._last_bounds = (vmin, vmax)

		# Persist the colormap definition to the user file.
		try:
			colours = [r["colour_picker"].get() for r in self._colour_rows]
			if self._is_interpolation():
				positions = [r["pos_var"].get() for r in self._colour_rows]
				positions[0] = vmin
				positions[-1] = vmax
				save_custom_cmap(name, "interpolation", colours, positions, vmin, vmax)
			else:
				lower_bounds = [r["pos_var"].get() for r in self._colour_rows]
				lower_bounds[0] = vmin
				save_custom_cmap(name, "bins", colours, lower_bounds, vmin, vmax)
		except Exception:
			CONSOLE_LOGGER.warning("Failed to persist colormap to file.", exc_info=True)

		if self.command is not None:
			self.command(cmap, (vmin, vmax))
		self._fire_on_change(cmap)

		if self._cmap_builder_window is not None:
			self._cmap_builder_window.close()

	def _close_builder(self) -> None:
		"""Reset popup state after the builder has been closed."""
		self._cmap_builder_window = None
		self._colour_rows = []

	# ------------------------------------------------------------------
	# BHoMBaseWidget interface
	# ------------------------------------------------------------------

	def get(self) -> Optional[Colormap]:
		"""Return the last applied colormap, or None if none has been built."""
		return self._last_cmap

	def get_bounds(self) -> tuple[float, float]:
		"""Return the (vmin, vmax) range of the last applied colormap."""
		return self._last_bounds

	def set(self, value: Colormap) -> None:
		"""Store a colormap as the current result."""
		self._last_cmap = value

	def validate(self) -> tuple[bool, Optional[str], Optional[Literal["info", "warning", "error"]]]:
		if self._last_cmap is None:
			return self.apply_validation((False, "No colormap has been built yet.", "error"))
		return self.apply_validation((True, None, None))

if __name__ == "__main__":
	from python_toolkit.bhom_tkinter.bhom_base_window import BHoMBaseWindow
	from python_toolkit.bhom_tkinter.widgets._packing_options import PackingOptions

	root = BHoMBaseWindow()
	parent_container = root.content_frame

	colour_picker = CmapBuilder(
		parent_container,
		alignment="center",
		build_options=PackingOptions(padx=10, pady=10),
	)
	colour_picker.build()

	root.mainloop()
