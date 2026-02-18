import tkinter as tk
from tkinter import ttk

import numpy as np

from entities import CABLE_LIBRARY
import models

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ApexShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apex Shield RF - Mission Simulator")

        # ---------------------------
        # Existing: Breakdown Voltage
        # ---------------------------
        tk.Label(root, text="Altitude (ft):").grid(row=0, column=0, sticky="w")
        self.alt_slider = tk.Scale(root, from_=0, to=70000, orient="horizontal", length=320)
        self.alt_slider.grid(row=0, column=1, sticky="we")

        tk.Label(root, text="Select Cable:").grid(row=1, column=0, sticky="w")
        self.cable_box = ttk.Combobox(root, values=list(CABLE_LIBRARY.keys()), state="readonly")
        self.cable_box.grid(row=1, column=1, sticky="we")
        self.cable_box.current(0)

        self.run_btn = tk.Button(root, text="Run Mission Check", command=self.update_results)
        self.run_btn.grid(row=2, column=0, columnspan=2, pady=(6, 6))

        self.result_label = tk.Label(root, text="Status: Ready", fg="blue")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        # ---------------------------
        # NEW: Phase Shift (Interactive)
        # ---------------------------
        ttk.Separator(root, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="we", pady=8)

        tk.Label(root, text="Phase Shift Simulator (G + ΔT)", font=("Segoe UI", 11, "bold")).grid(
            row=5, column=0, columnspan=2, pady=(0, 6)
        )

        # Inputs for phase shift model
        tk.Label(root, text="Frequency (GHz):").grid(row=6, column=0, sticky="w")
        self.freq_slider = tk.Scale(root, from_=0.1, to=10.0, resolution=0.1, orient="horizontal",
                                    length=320, command=self.on_phase_change)
        self.freq_slider.set(1.0)
        self.freq_slider.grid(row=6, column=1, sticky="we")

        tk.Label(root, text="Cable length (m):").grid(row=7, column=0, sticky="w")
        self.length_slider = tk.Scale(root, from_=0.1, to=30.0, resolution=0.1, orient="horizontal",
                                      length=320, command=self.on_phase_change)
        self.length_slider.set(5.0)
        self.length_slider.grid(row=7, column=1, sticky="we")

        tk.Label(root, text="ΔT (°C):").grid(row=8, column=0, sticky="w")
        self.temp_slider = tk.Scale(root, from_=-50, to=150, resolution=1, orient="horizontal",
                                    length=320, command=self.on_phase_change)
        self.temp_slider.set(0)
        self.temp_slider.grid(row=8, column=1, sticky="we")

        tk.Label(root, text="G-load:").grid(row=9, column=0, sticky="w")
        self.g_slider = tk.Scale(root, from_=1.0, to=9.0, resolution=0.1, orient="horizontal",
                                 length=320, command=self.on_phase_change)
        self.g_slider.set(1.0)
        self.g_slider.grid(row=9, column=1, sticky="we")

        # Routing model parameters (simple + interactive)
        tk.Label(root, text="# spans (clamp sections):").grid(row=10, column=0, sticky="w")
        self.spans_slider = tk.Scale(root, from_=1, to=30, resolution=1, orient="horizontal",
                                     length=320, command=self.on_phase_change)
        self.spans_slider.set(10)
        self.spans_slider.grid(row=10, column=1, sticky="we")

        tk.Label(root, text="Clamp spacing D (m):").grid(row=11, column=0, sticky="w")
        self.spacing_slider = tk.Scale(root, from_=0.1, to=2.0, resolution=0.1, orient="horizontal",
                                       length=320, command=self.on_phase_change)
        self.spacing_slider.set(0.5)
        self.spacing_slider.grid(row=11, column=1, sticky="we")

        tk.Label(root, text="Sag @1G (mm):").grid(row=12, column=0, sticky="w")
        self.sag_slider = tk.Scale(root, from_=0.0, to=10.0, resolution=0.1, orient="horizontal",
                                   length=320, command=self.on_phase_change)
        self.sag_slider.set(2.0)
        self.sag_slider.grid(row=12, column=1, sticky="we")

        # Material-ish parameters (start with defaults; you can later store per-cable values)
        self.epsilon_r = 2.1          # PTFE-ish default
        self.alpha_per_C = 1.7e-5     # 17 ppm/°C default (effective)

        self.phase_value = tk.Label(root, text="ΔPhase: 0.00°", fg="purple")
        self.phase_value.grid(row=13, column=0, columnspan=2, pady=(6, 6))

        # Plot (Δphase vs frequency)
        self.fig = Figure(figsize=(6.2, 3.0), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Frequency (GHz)")
        self.ax.set_ylabel("Phase shift (deg)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=14, column=0, columnspan=2, sticky="we", pady=(0, 10))

        # Make UI stretch nicely
        root.grid_columnconfigure(1, weight=1)

        # Initial plot
        self.on_phase_change()

    # ---------------------------
    # Existing breakdown voltage
    # ---------------------------
    def update_results(self):
        alt = self.alt_slider.get()
        cable_id = self.cable_box.get()
        spec = CABLE_LIBRARY[cable_id]

        pressure = 101.325 * (2.718 ** (-0.0000366 * alt))
        gap = spec["D"] - spec["d"]
        v_limit = models.paschen_breakdown_voltage(pressure, gap)

        self.result_label.config(text=f"Breakdown Limit: {v_limit:.1f}V")

    # ---------------------------
    # NEW: Interactive phase
    # ---------------------------
    def on_phase_change(self, *_):
        f_ghz = float(self.freq_slider.get())
        f_hz = f_ghz * 1e9

        L = float(self.length_slider.get())
        dT = float(self.temp_slider.get())
        G = float(self.g_slider.get())

        N = int(float(self.spans_slider.get()))
        D = float(self.spacing_slider.get())
        sag1_mm = float(self.sag_slider.get())
        sag1_m = sag1_mm / 1000.0

        # Calculate phase shift for current slider point
        dphi_deg = models.phase_shift_deg_routing_and_temp(
            frequency_hz=f_hz,
            total_length_m=L,
            epsilon_r=self.epsilon_r,
            deltaT_C=dT,
            g_load=G,
            alpha_per_C=self.alpha_per_C,
            N_spans=N,
            clamp_spacing_m=D,
            sag1_m=sag1_m
        )

        self.phase_value.config(text=f"ΔPhase @ {f_ghz:.1f} GHz: {dphi_deg:.2f}°")

        # Plot Δphase vs frequency (0.1–10 GHz)
        freqs = np.linspace(0.1, 10.0, 200)
        ys = []
        for fg in freqs:
            ys.append(models.phase_shift_deg_routing_and_temp(
                frequency_hz=fg * 1e9,
                total_length_m=L,
                epsilon_r=self.epsilon_r,
                deltaT_C=dT,
                g_load=G,
                alpha_per_C=self.alpha_per_C,
                N_spans=N,
                clamp_spacing_m=D,
                sag1_m=sag1_m
            ))

        self.ax.clear()
        self.ax.plot(freqs, ys)
        self.ax.set_xlabel("Frequency (GHz)")
        self.ax.set_ylabel("Phase shift (deg)")
        self.ax.grid(True)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = ApexShieldApp(root)
    root.mainloop()
