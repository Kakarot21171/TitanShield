import tkinter as tk
from tkinter import ttk

from entities import CABLE_LIBRARY
from models import compute_phase_deg, sweep_phase_vs_freq
from visualizer import PlotPanel


class TitanShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TitanShield - Phase Shift Simulator")
        self.geometry("1100x650")

        # Root layout: controls (left) + plot (right)
        self.columnconfigure(0, weight=0)  # controls
        self.columnconfigure(1, weight=1)  # plot
        self.rowconfigure(0, weight=1)

        self.controls = ttk.Frame(self, padding=10)
        self.controls.grid(row=0, column=0, sticky="nsw")

        self.plot_panel = PlotPanel(self)
        self.plot_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Status: Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="center")
        status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # Vars
        cable_names = list(CABLE_LIBRARY.keys())
        self.cable_var = tk.StringVar(value=cable_names[0] if cable_names else "")

        self.freq_var = tk.DoubleVar(value=1.0)
        self.length_var = tk.DoubleVar(value=5.0)
        self.dt_var = tk.DoubleVar(value=0.0)
        self.g_var = tk.DoubleVar(value=1.0)
        self.spans_var = tk.IntVar(value=10)
        self.spacing_var = tk.DoubleVar(value=0.5)
        self.sag_var = tk.DoubleVar(value=2.0)

        # Frequency sweep settings (for the plot)
        self.f_start_var = tk.DoubleVar(value=0.1)
        self.f_stop_var = tk.DoubleVar(value=3.0)
        self.f_points_var = tk.IntVar(value=200)

        self._build_controls()
        self._recompute_and_draw()

    def _build_controls(self):
        # Title
        ttk.Label(
            self.controls,
            text="Phase Shift Simulator (G + ΔT)",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # Make the control grid compact
        for c in range(4):
            self.controls.columnconfigure(c, weight=0)

        # ---- Row 1: Cable + Current Frequency readout (single-point) ----
        ttk.Label(self.controls, text="Cable Type:").grid(row=1, column=0, sticky="w")
        cable_box = ttk.Combobox(
            self.controls,
            textvariable=self.cable_var,
            values=list(CABLE_LIBRARY.keys()),
            state="readonly",
            width=16
        )
        cable_box.grid(row=1, column=1, sticky="w", padx=(6, 14))
        cable_box.bind("<<ComboboxSelected>>", lambda e: self._recompute_and_draw())

        ttk.Label(self.controls, text="Marker Freq (GHz):").grid(row=1, column=2, sticky="w")
        self._make_slider(
            row=1, col=3,
            var=self.freq_var,
            minv=0.1, maxv=10.0,
            step=0.1
        )

        # ---- Row 2: Length + ΔT ----
        ttk.Label(self.controls, text="Cable length (m):").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self._make_slider(row=2, col=1, var=self.length_var, minv=0.1, maxv=100.0, step=0.1, pady=(6, 0))

        ttk.Label(self.controls, text="ΔT (°C):").grid(row=2, column=2, sticky="w", pady=(6, 0))
        self._make_slider(row=2, col=3, var=self.dt_var, minv=-100.0, maxv=200.0, step=1.0, pady=(6, 0))

        # ---- Row 3: G-load + spans ----
        ttk.Label(self.controls, text="G-load:").grid(row=3, column=0, sticky="w", pady=(6, 0))
        self._make_slider(row=3, col=1, var=self.g_var, minv=0.0, maxv=15.0, step=0.1, pady=(6, 0))

        ttk.Label(self.controls, text="# spans:").grid(row=3, column=2, sticky="w", pady=(6, 0))
        self._make_slider(row=3, col=3, var=self.spans_var, minv=0, maxv=50, step=1, pady=(6, 0), is_int=True)

        # ---- Row 4: clamp spacing + sag ----
        ttk.Label(self.controls, text="Clamp spacing D (m):").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self._make_slider(row=4, col=1, var=self.spacing_var, minv=0.05, maxv=5.0, step=0.05, pady=(6, 0))

        ttk.Label(self.controls, text="Sag @1G (mm):").grid(row=4, column=2, sticky="w", pady=(6, 0))
        self._make_slider(row=4, col=3, var=self.sag_var, minv=0.0, maxv=50.0, step=0.1, pady=(6, 0))

        # ---- Sweep controls (small) ----
        sep = ttk.Separator(self.controls, orient="horizontal")
        sep.grid(row=5, column=0, columnspan=4, sticky="ew", pady=10)

        ttk.Label(self.controls, text="Plot Sweep:").grid(row=6, column=0, sticky="w")

        ttk.Label(self.controls, text="Start (GHz):").grid(row=7, column=0, sticky="w")
        ttk.Entry(self.controls, textvariable=self.f_start_var, width=10).grid(row=7, column=1, sticky="w", padx=(6, 14))

        ttk.Label(self.controls, text="Stop (GHz):").grid(row=7, column=2, sticky="w")
        ttk.Entry(self.controls, textvariable=self.f_stop_var, width=10).grid(row=7, column=3, sticky="w", padx=(6, 0))

        ttk.Label(self.controls, text="Points:").grid(row=8, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(self.controls, textvariable=self.f_points_var, width=10).grid(row=8, column=1, sticky="w", padx=(6, 14), pady=(6, 0))

        ttk.Button(self.controls, text="Recompute / Redraw", command=self._recompute_and_draw)\
            .grid(row=9, column=0, columnspan=4, sticky="ew", pady=(10, 0))

        # Marker output (single point)
        self.marker_label = ttk.Label(self.controls, text="ΔPhase @ marker: 0.00°")
        self.marker_label.grid(row=10, column=0, columnspan=4, sticky="w", pady=(10, 0))

    def _make_slider(self, row, col, var, minv, maxv, step, pady=(0, 0), is_int=False):
        # Slider + value label inside a small frame
        frame = ttk.Frame(self.controls)
        frame.grid(row=row, column=col, sticky="w", pady=pady)

        # Value label
        val_lbl = ttk.Label(frame, width=6, anchor="e")
        val_lbl.pack(side="left")

        def on_change(_=None):
            # update value label
            v = var.get()
            if is_int:
                v = int(round(float(v)))
                var.set(v)
                val_lbl.config(text=str(v))
            else:
                val_lbl.config(text=f"{float(v):.2f}")
            self._recompute_and_draw()

        # Slider
        resolution = step
        scale = ttk.Scale(frame, from_=minv, to=maxv, variable=var, command=lambda e: on_change())
        scale.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Initialize value label
        on_change()

    def _gather_params(self):
        return dict(
            length_m=float(self.length_var.get()),
            delta_t_c=float(self.dt_var.get()),
            g_load=float(self.g_var.get()),
            spans=int(self.spans_var.get()),
            clamp_spacing_m=float(self.spacing_var.get()),
            sag_at_1g_mm=float(self.sag_var.get()),
            cable_type=self.cable_var.get(),
        )

    def _recompute_and_draw(self):
        try:
            params = self._gather_params()

            # marker (single freq)
            dphi_marker = compute_phase_deg(
                freq_ghz=float(self.freq_var.get()),
                **params
            )
            self.marker_label.config(text=f"ΔPhase @ {self.freq_var.get():.2f} GHz: {dphi_marker:.2f}°")

            # sweep plot
            f_start = float(self.f_start_var.get())
            f_stop = float(self.f_stop_var.get())
            n = int(self.f_points_var.get())

            freqs, phases = sweep_phase_vs_freq(
                f_start_ghz=f_start,
                f_stop_ghz=f_stop,
                n=n,
                **params
            )

            title = f"{params['cable_type']} | L={params['length_m']:.2f}m | ΔT={params['delta_t_c']:.1f}°C | G={params['g_load']:.1f}"
            self.plot_panel.plot(freqs, phases, title=title)

            self.status_var.set("Status: Ready")

        except Exception as e:
            self.status_var.set(f"Status: Error - {e}")
