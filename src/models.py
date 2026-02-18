import math
from entities import CABLE_LIBRARY

C = 299_792_458.0  # speed of light m/s


def compute_phase_deg(
    freq_ghz: float,
    length_m: float,
    delta_t_c: float,
    g_load: float,
    spans: int,
    clamp_spacing_m: float,
    sag_at_1g_mm: float,
    cable_type: str,
) -> float:
    """
    Simple model:
      - Base phase = 360 * (electrical_length / wavelength)
      - Temperature changes electrical length via temp coeff (ppm/°C).
      - G-load changes sag -> increases path length slightly.
    Returns delta phase (degrees) relative to baseline (ΔT=0, G=1).
    """

    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    f_hz = freq_ghz * 1e9
    if f_hz <= 0:
        return 0.0

    # Baseline electrical length
    v = C * cable.velocity_factor
    wavelength = v / f_hz

    # Helper to compute effective physical length under sag
    def effective_length_under_g(g: float) -> float:
        # sag scales ~ linearly with g in this simple approximation
        sag_m = (sag_at_1g_mm / 1000.0) * max(g, 0.0)

        # approximate extra length per span via small-sag parabola arc length:
        # ΔL ≈ (8 * sag^2) / (3 * span_length)
        # where span_length = clamp_spacing_m
        span_len = max(clamp_spacing_m, 1e-6)
        extra_per_span = (8.0 * sag_m * sag_m) / (3.0 * span_len)

        total_extra = extra_per_span * max(spans, 0)
        return max(length_m + total_extra, 0.0)

    # Baseline (ΔT=0, G=1)
    L0 = effective_length_under_g(1.0)

    # New length under current g
    Lg = effective_length_under_g(g_load)

    # Temperature effect on electrical length (ppm/°C)
    # Electrical length multiplier:
    temp_multiplier = 1.0 + (cable.temp_coeff_ppm_per_c * 1e-6 * delta_t_c)

    # Electrical lengths
    e0 = L0
    e1 = Lg * temp_multiplier

    # Phase
    phi0 = 360.0 * (e0 / wavelength)
    phi1 = 360.0 * (e1 / wavelength)

    # Delta phase (wrap to [-180, 180] for nicer display)
    dphi = phi1 - phi0
    dphi = (dphi + 180.0) % 360.0 - 180.0
    return dphi


def sweep_phase_vs_freq(
    f_start_ghz: float,
    f_stop_ghz: float,
    n: int,
    **kwargs,
):
    if n < 2:
        n = 2
    f0 = min(f_start_ghz, f_stop_ghz)
    f1 = max(f_start_ghz, f_stop_ghz)
    step = (f1 - f0) / (n - 1)

    freqs = []
    phases = []
    for i in range(n):
        f = f0 + i * step
        freqs.append(f)
        phases.append(compute_phase_deg(freq_ghz=f, **kwargs))
    return freqs, phases
