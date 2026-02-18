import matplotlib.pyplot as plt
from main import run_mission_simulation


def plot_mission_risk():
    # Metrics to track
    altitudes = range(0, 70001, 5000)
    breakdown_voltages = []

    # Run simulation loop to collect data
    for alt in altitudes:
        result = run_mission_simulation(altitude=alt, op_voltage=1500, interference_vm=5000)
        breakdown_voltages.append(result["Breakdown_V"])

    # Generate Analyzable Result: The "Safety Margin" Graph
    plt.figure(figsize=(10, 6))
    plt.plot(altitudes, breakdown_voltages, 'r-o', label='Arcing Threshold (Vb)')
    plt.axhline(y=1500, color='b', linestyle='--', label='Operating Voltage (1500V)')

    # Custom Logic: Highlight the Failure Zone
    plt.fill_between(altitudes, 0, 1500, color='red', alpha=0.2, label='Failure Zone')

    plt.title("Apex Shield RF: Dielectric Breakdown vs. Altitude")
    plt.xlabel("Altitude (ft)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    plot_mission_risk()