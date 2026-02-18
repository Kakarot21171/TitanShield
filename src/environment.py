import numpy as np

def check_altitude_failure(self, altitude_ft, operating_voltage):
    # Algorithm 2: Paschen's Law

    # 1. Convert altitude to pressure (simplified barometric formula)
    pressure = 101.325 * np.exp(-0.0000366 * altitude_ft)  # kPa

    # 2. Define constants for air
    A, B = 11.25, 273.75
    gamma_se = 0.01  # Secondary electron emission coefficient
    gap = self.D - self.d  # Distance between core and shield

    # 3. Calculate Breakdown Voltage (Vb)
    Pd = pressure * gap
    Vb = (B * Pd) / (np.log(A * Pd) - np.log(np.log(1 + 1 / gamma_se)))

    # 4. Interaction: Check if system fails
    if operating_voltage > Vb:
        return "CATASTROPHIC FAILURE: Dielectric Breakdown (Arcing)"
    return "SAFE: Voltage below breakdown threshold"