from entities import CoaxLine, Atmosphere
import models


def run_mission_simulation(altitude, op_voltage, interference_vm):
    # 1. Initialize Entities
    cable = CoaxLine("RG-400", 0.0009, 0.0029, 2.1, 5.8e7, 90)
    env = Atmosphere(altitude)

    # 2. Interactions: Environmental impact on cable
    v_limit = models.paschen_breakdown_voltage(env.pressure, cable.gap)
    leakage = models.calculate_shielding_leakage(interference_vm, cable.se_db)

    # 3. Data Collection: Metrics to track
    status = "SUCCESS"
    if op_voltage > v_limit:
        status = "FAILED: ARCOVER"
    elif leakage > 0.001:  # Threshold for sensitive receivers
        status = "FAILED: NOISE INTERFERENCE"

    return {
        "Altitude": altitude,
        "Breakdown_V": round(v_limit, 2),
        "Noise_Ingress": round(leakage, 6),
        "Status": status
    }

if __name__ == "__main__":
    print(run_mission_simulation(altitude=55000, op_voltage=1500, interference_vm=5000))
