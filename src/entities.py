from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CoaxCable:
    name: str

    # Existing properties
    velocity_factor: float
    alpha_db_per_m: float
    temp_coeff_ppm_per_c: float

    # New dielectric model properties
    epsilon_r_ref: float                  # reference dielectric constant
    epsilon_temp_coeff_per_c: float       # fractional change per °C
    epsilon_freq_coeff: float             # fractional log-frequency effect

    # New shielding model properties
    shield_db_ref_1ghz: float             # shielding effectiveness at 1 GHz
    shield_slope_db_per_decade: float     # degradation per frequency decade

    # New impedance properties
    nominal_impedance_ohm: float          # usually 50 ohm or 75 ohm


CABLE_LIBRARY = {
    "RG-58": CoaxCable(
        name="RG-58",
        velocity_factor=0.66,
        alpha_db_per_m=0.20,
        temp_coeff_ppm_per_c=50.0,

        epsilon_r_ref=2.30,
        epsilon_temp_coeff_per_c=0.0004,
        epsilon_freq_coeff=0.015,

        shield_db_ref_1ghz=55.0,
        shield_slope_db_per_decade=8.0,

        nominal_impedance_ohm=50.0,
    ),
    "RG-213": CoaxCable(
        name="RG-213",
        velocity_factor=0.66,
        alpha_db_per_m=0.12,
        temp_coeff_ppm_per_c=45.0,

        epsilon_r_ref=2.25,
        epsilon_temp_coeff_per_c=0.00035,
        epsilon_freq_coeff=0.012,

        shield_db_ref_1ghz=65.0,
        shield_slope_db_per_decade=6.0,

        nominal_impedance_ohm=50.0,
    ),
    "LMR-400": CoaxCable(
        name="LMR-400",
        velocity_factor=0.85,
        alpha_db_per_m=0.07,
        temp_coeff_ppm_per_c=20.0,

        epsilon_r_ref=1.38,
        epsilon_temp_coeff_per_c=0.0002,
        epsilon_freq_coeff=0.008,

        shield_db_ref_1ghz=90.0,
        shield_slope_db_per_decade=4.0,

        nominal_impedance_ohm=50.0,
    ),
}
