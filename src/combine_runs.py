import csv
from pathlib import Path

RUNS_DIR = Path(__file__).resolve().parent.parent / "runs"
OUTPUT_FILE = RUNS_DIR / "all_runs.csv"


def combine_all_runs():
    all_data = []

    # Loop through all CSV files
    for file in sorted(RUNS_DIR.glob("run_*_timeseries.csv")):

        run_id = file.stem.split("_")[1]  # extracts 001, 002, etc.

        with open(file, "r") as f:
            reader = csv.DictReader(f)

            for row in reader:
                all_data.append({
                    "run_id": run_id,
                    "timestamp": row["timestamp"],
                    "frequency_GHz": row["frequency_GHz"],
                    "phase_deg": row["phase_deg"]
                })

    # Write combined CSV
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_id", "timestamp", "frequency_GHz", "phase_deg"]
        )

        writer.writeheader()
        writer.writerows(all_data)

    print(f"Combined file created: {OUTPUT_FILE}")


if __name__ == "__main__":
    combine_all_runs()