import json
import csv
import time
from datetime import datetime
from pathlib import Path

from models import sweep_phase_vs_freq


RUN_PLAN_FILE = "run_plan.json"
OUTPUT_DIR = Path("runs")


def run_simulations():
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(RUN_PLAN_FILE, "r") as f:
        run_plan = json.load(f)

    for i, params in enumerate(run_plan, start=1):

        run_id = f"{i:03d}"
        print(f"Running simulation {run_id}...")

        start_time = time.time()

        freqs, phases = sweep_phase_vs_freq(
            f_start_ghz=params["f_start_ghz"],
            f_stop_ghz=params["f_stop_ghz"],
            n=params["points"],
            length_m=params["length_m"],
            delta_t_c=params["delta_t_c"],
            g_load=params["g_load"],
            spans=params["spans"],
            clamp_spacing_m=params["clamp_spacing_m"],
            sag_at_1g_mm=params["sag_at_1g_mm"],
            cable_type=params["cable_type"],
        )

        duration = time.time() - start_time
        timestamp = datetime.now().isoformat()

        csv_file = OUTPUT_DIR / f"run_{run_id}_timeseries.csv"
        json_file = OUTPUT_DIR / f"run_{run_id}_summary.json"

        # Write CSV time series
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "frequency_GHz", "phase_deg"])

            for fghz, phase in zip(freqs, phases):
                writer.writerow([timestamp, fghz, phase])

        # Summary statistics
        summary = {
            "run_id": run_id,
            "timestamp": timestamp,
            "parameters": params,
            "duration_sec": duration,
            "status": "Complete",
            "max_phase_deg": max(phases),
            "min_phase_deg": min(phases),
            "avg_phase_deg": sum(phases) / len(phases),
            "data_file": str(csv_file),
        }

        with open(json_file, "w") as f:
            json.dump(summary, f, indent=4)

        print(f"Completed run {run_id} in {duration:.3f} seconds")


if __name__ == "__main__":
    run_simulations()