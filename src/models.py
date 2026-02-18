import math
import numpy as np

# Speed of light in vacuum (m/s)
C0 = 299_792_458.0


# -----------------------------
# Model 1: Signal Integrity
# -----------------------------
def calculate_attenuation(frequency_ghz, d, sigma, epsilon_r):
    """
    Calculates a simple conductor-loss-like attenuation term based on skin effect.
    NOTE: This is a simplified placeholder model.
    """
    return (1 / (d * sigma)) * np.sqrt(frequency_ghz * 1e9)


# -----------------------------
# Model 2: Atmospheric Failure
# -----------------------------
def paschen_breakdown_voltage(pressure_kpa, gap_m):
    """
    Calculates the arcing threshold using Paschen's Law (simplified form).
    Returns breakdown voltage in volts.
    """
    A, B = 11.25, 273.75
    gamma_se = 0.01  # Secondary electron emission coefficient

    pd = pressure_kpa * gap_m
    if pd <= 0:
        return 0

    numerator = B * pd
    denominator = np.log(A * pd) - np.log(np.log(1 + 1 / gamma_se))
    # Avoid division by zero / invalid values
    if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
        return 0

    return float(numerator / denominator)


# -----------------------------
# Model 3: Electronic Warfare (Ingress)
# -----------------------------
def calculate_shielding_leakage(external_field_vm, shielding_effectiveness_db):
    """
    Calculates how much noise leaks past the shield based on shielding effectiveness (dB).
    """
    reduction_factor = 10 ** (shielding_effectiveness_db / 20)
    return external_field_vm / reduction_factor


# -----------------------------
# Model 4: Phase / Timing Effects
# -----------------------------
def phase_shift_deg(
    frequency_hz: float,
    length_m: float,
    epsilon_r: float,
    deltaT_C: float,
    g_load: float,
    alpha_per_C: float = 1.7e-5,        # ~17 ppm/°C (tunable effective expansion)
    k_eps_per_C: float = 0.0,           # dielectric temp coefficient: Δεr per °C (tunable)
    k_g_strain_per_g: float = 0.0       # fractional strain per +1G over 1G (tunable)
) -> float:
    """
    Returns phase shift (degrees) caused by ΔT and g-load using a simple parametric model.

    Base:
      φ = βL, β = 2πf / vp, vp = c / sqrt(εr)

    Effects:
      - Thermal expansion: ΔL/L ≈ αΔT
      - G-induced axial strain: ΔL/L ≈ k_g*(G-1)
      - Dielectric temp shift: εr -> εr + k_eps*ΔT
    """
    if frequency_hz <= 0 or length_m <= 0 or epsilon_r <= 0:
        return 0.0

    # Baseline propagation
    vp0 = C0 / math.sqrt(epsilon_r)
    beta0 = 2.0 * math.pi * frequency_hz / vp0
    phi0 = beta0 * length_m  # radians

    # Length change: thermal + g-induced strain
    frac_dL = alpha_per_C * deltaT_C + k_g_strain_per_g * max(0.0, (g_load - 1.0))
    L1 = length_m * (1.0 + frac_dL)

    # Permittivity change with temperature
    eps1 = max(1e-12, epsilon_r + k_eps_per_C * deltaT_C)

    vp1 = C0 / math.sqrt(eps1)
    beta1 = 2.0 * math.pi * frequency_hz / vp1
    phi1 = beta1 * L1

    dphi_rad = phi1 - phi0
    return math.degrees(dphi_rad)


# -----------------------------
# Model 5: Routing-based 9G model (interactive-friendly)
# -----------------------------
def routing_delta_length_m(G: float, N_spans: int, clamp_spacing_m: float, sag1_m: float) -> float:
    """
    Extra effective length change from 1G to G due to sag between clamps.

    Assumptions:
      - Cable between clamps bows as a shallow parabola.
      - Span chord length = D
      - Mid-span sag = s(G)
      - For shallow sag: L_span ≈ D + (8 s^2)/(3D)
      - Use s(G) = sag1 * G, then subtract baseline at 1G.

    Returns ΔL_total (meters) relative to 1G.
    """
    if N_spans <= 0 or clamp_spacing_m <= 0 or sag1_m < 0:
        return 0.0

    G = max(1.0, float(G))
    D = float(clamp_spacing_m)
    s1 = float(sag1_m)

    # ΔL per span from 1G to G:
    # (8/(3D)) * ( (s1*G)^2 - (s1*1)^2 ) = (8*s1^2/(3D)) * (G^2 - 1)
    per_span = (8.0 * (s1 ** 2) / (3.0 * D)) * ((G ** 2) - 1.0)
    return float(N_spans * per_span)


def phase_shift_deg_routing_and_temp(
    frequency_hz: float,
    total_length_m: float,
    epsilon_r: float,
    deltaT_C: float,
    g_load: float,
    alpha_per_C: float,
    N_spans: int,
    clamp_spacing_m: float,
    sag1_m: float
) -> float:
    """
    Phase shift (degrees) caused by:
      - Temperature expansion of the whole cable: ΔL_T = α * L * ΔT
      - Routing/sag change under G: ΔL_G from routing_delta_length_m()

    Δφ ≈ β * (ΔL_T + ΔL_G), then convert to degrees.
    """
    if frequency_hz <= 0 or total_length_m <= 0 or epsilon_r <= 0:
        return 0.0

    vp = C0 / math.sqrt(epsilon_r)
    beta = 2.0 * math.pi * frequency_hz / vp  # rad/m

    dL_temp = float(alpha_per_C) * float(total_length_m) * float(deltaT_C)
    dL_route = routing_delta_length_m(g_load, N_spans, clamp_spacing_m, sag1_m)

    dphi_rad = beta * (dL_temp + dL_route)
    return math.degrees(dphi_rad)
