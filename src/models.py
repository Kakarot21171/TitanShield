import math
from entities import CABLE_LIBRARY

C = 299_792_458.0  # speed of light (m/s)


def _effective_length_under_g(length_m, g_load, spans, clamp_spacing_m, sag_at_1g_mm):
    """
    Small-sag parabola approximation for extra path length.
    """
    sag_m = (sag_at_1g_mm / 1000.0) * max(g_load, 0.0)
    span_len = max(clamp_spacing_m, 1e-6)

    # ΔL ≈ (8 * sag^2) / (3 * span_length)
    extra_per_span = (8.0 * sag_m * sag_m) / (3.0 * span_len)
    total_extra = extra_per_span * max(spans, 0)

    return max(length_m + total_extra, 0.0)


def effective_dielectric_constant(cable_type: str, freq_ghz: float, delta_t_c: float) -> float:
    """
    Simple dielectric model:
      epsilon_eff = epsilon_ref
                    * (1 + temp_term)
                    * (1 + freq_term)

    freq_term uses log10(f / 1 GHz) so the effect changes gradually with frequency.
    """
    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    f = max(freq_ghz, 1e-6)

    temp_multiplier = 1.0 + cable.epsilon_temp_coeff_per_c * delta_t_c
    freq_multiplier = 1.0 + cable.epsilon_freq_coeff * math.log10(f / 1.0)

    eps_eff = cable.epsilon_r_ref * temp_multiplier * freq_multiplier
    return max(eps_eff, 1.0001)


def effective_velocity_factor(cable_type: str, freq_ghz: float, delta_t_c: float) -> float:
    """
    Adjust velocity factor from dielectric shift.
    Uses the cable's reference dielectric constant as the baseline.
    """
    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    eps_eff = effective_dielectric_constant(cable_type, freq_ghz, delta_t_c)

    # Relative scaling from reference epsilon
    vf_eff = cable.velocity_factor * math.sqrt(cable.epsilon_r_ref / eps_eff)

    # Keep it physically sane
    return min(max(vf_eff, 0.01), 0.99)


def compute_shielding_db(freq_ghz: float, cable_type: str) -> float:
    """
    Simple frequency-dependent shielding model:
      SE(f) = SE_ref - slope * log10(f / 1 GHz)

    Higher frequency -> lower shielding effectiveness.
    """
    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    f = max(freq_ghz, 1e-6)
    se_db = cable.shield_db_ref_1ghz - cable.shield_slope_db_per_decade * math.log10(f / 1.0)

    return max(se_db, 0.0)


def compute_characteristic_impedance(cable_type: str, freq_ghz: float, delta_t_c: float) -> float:
    """
    Approximate impedance drift from dielectric shift.
    Since Z0 ~ 1/sqrt(epsilon_r), we scale nominal impedance accordingly.
    """
    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    eps_eff = effective_dielectric_constant(cable_type, freq_ghz, delta_t_c)
    z0 = cable.nominal_impedance_ohm * math.sqrt(cable.epsilon_r_ref / eps_eff)
    return z0


def compute_mismatch_metrics(z0_ohm: float, z_load_ohm: float = 50.0):
    """
    Reflection coefficient, return loss, VSWR, mismatch loss.
    """
    z0 = max(z0_ohm, 1e-9)
    zl = max(z_load_ohm, 1e-9)

    gamma = abs((zl - z0) / (zl + z0))

    if gamma >= 1.0:
        gamma = 0.999999

    return_loss_db = -20.0 * math.log10(max(gamma, 1e-12))
    vswr = (1.0 + gamma) / (1.0 - gamma)
    mismatch_loss_db = -10.0 * math.log10(1.0 - gamma * gamma)

    return {
        "gamma": gamma,
        "return_loss_db": return_loss_db,
        "vswr": vswr,
        "mismatch_loss_db": mismatch_loss_db,
    }


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
    Upgraded phase model:
      - Baseline phase uses baseline effective length at ΔT=0, G=1
      - New phase uses:
          * sag-adjusted length under G-load
          * temperature/frequency-adjusted dielectric shift via VF
      - Also preserves your original cable temp_coeff_ppm_per_c effect
    """
    cable = CABLE_LIBRARY.get(cable_type)
    if cable is None:
        raise ValueError(f"Unknown cable_type: {cable_type}")

    f_hz = freq_ghz * 1e9
    if f_hz <= 0:
        return 0.0

    # Baseline geometry
    L0 = _effective_length_under_g(
        length_m=length_m,
        g_load=1.0,
        spans=spans,
        clamp_spacing_m=clamp_spacing_m,
        sag_at_1g_mm=sag_at_1g_mm,
    )

    # Loaded geometry
    Lg = _effective_length_under_g(
        length_m=length_m,
        g_load=g_load,
        spans=spans,
        clamp_spacing_m=clamp_spacing_m,
        sag_at_1g_mm=sag_at_1g_mm,
    )

    # Existing electrical-length temperature multiplier
    temp_length_multiplier = 1.0 + (cable.temp_coeff_ppm_per_c * 1e-6 * delta_t_c)

    # Baseline VF and updated VF
    vf0 = effective_velocity_factor(cable_type, freq_ghz, 0.0)
    vf1 = effective_velocity_factor(cable_type, freq_ghz, delta_t_c)

    wavelength0 = (C * vf0) / f_hz
    wavelength1 = (C * vf1) / f_hz

    e0 = L0
    e1 = Lg * temp_length_multiplier

    phi0 = 360.0 * (e0 / wavelength0)
    phi1 = 360.0 * (e1 / wavelength1)

    dphi = phi1 - phi0
    dphi = (dphi + 180.0) % 360.0 - 180.0
    return dphi


def compute_marker_metrics(
    freq_ghz: float,
    length_m: float,
    delta_t_c: float,
    g_load: float,
    spans: int,
    clamp_spacing_m: float,
    sag_at_1g_mm: float,
    cable_type: str,
    z_load_ohm: float = 50.0,
):
    """
    One-stop metrics for the UI.
    """
    phase_deg = compute_phase_deg(
        freq_ghz=freq_ghz,
        length_m=length_m,
        delta_t_c=delta_t_c,
        g_load=g_load,
        spans=spans,
        clamp_spacing_m=clamp_spacing_m,
        sag_at_1g_mm=sag_at_1g_mm,
        cable_type=cable_type,
    )

    eps_eff = effective_dielectric_constant(cable_type, freq_ghz, delta_t_c)
    vf_eff = effective_velocity_factor(cable_type, freq_ghz, delta_t_c)
    shielding_db = compute_shielding_db(freq_ghz, cable_type)
    z0 = compute_characteristic_impedance(cable_type, freq_ghz, delta_t_c)
    mismatch = compute_mismatch_metrics(z0, z_load_ohm)

    return {
        "phase_deg": phase_deg,
        "epsilon_eff": eps_eff,
        "vf_eff": vf_eff,
        "shielding_db": shielding_db,
        "z0_ohm": z0,
        "gamma": mismatch["gamma"],
        "return_loss_db": mismatch["return_loss_db"],
        "vswr": mismatch["vswr"],
        "mismatch_loss_db": mismatch["mismatch_loss_db"],
    }


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
