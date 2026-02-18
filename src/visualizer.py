import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Frequency (GHz)")
        self.ax.set_ylabel("Δ Phase (deg)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._line = None

    def plot(self, x, y, title=None):
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_xlabel("Frequency (GHz)")
        self.ax.set_ylabel("Δ Phase (deg)")
        if title:
            self.ax.set_title(title)

        self.ax.plot(x, y)
        self.canvas.draw()
