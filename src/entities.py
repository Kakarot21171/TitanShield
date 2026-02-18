from dataclasses import dataclass


@dataclass(frozen=True)
class CoaxCable:
    name: str
    velocity_factor: float   # fraction of speed of light
    alpha_db_per_m: float    # simple attenuation (not required for phase shift, but handy)
    temp_coeff_ppm_per_c: float  # ppm/°C change in electrical length (effective VF shift)


# Example library (edit to match your cables)
CABLE_LIBRARY = {
    "RG-58": CoaxCable(
        name="RG-58",
        velocity_factor=0.66,
        alpha_db_per_m=0.20,
        temp_coeff_ppm_per_c=50.0,
    ),
    "RG-213": CoaxCable(
        name="RG-213",
        velocity_factor=0.66,
        alpha_db_per_m=0.12,
        temp_coeff_ppm_per_c=45.0,
    ),
    "LMR-400": CoaxCable(
        name="LMR-400",
        velocity_factor=0.85,
        alpha_db_per_m=0.07,
        temp_coeff_ppm_per_c=20.0,
    ),
}
