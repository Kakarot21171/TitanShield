import numpy as np

CABLE_LIBRARY = {
    "RG-400": {"name": "RG-400 (Standard)", "d": 0.0009, "D": 0.0029, "se": 90},
    "RG-393": {"name": "RG-393 (High Power)", "d": 0.0024, "D": 0.0072, "se": 80},
    "Semi-Rigid": {"name": "Semi-Rigid (Space)", "d": 0.0005, "D": 0.0016, "se": 110}
}

class CoaxLine:
    def __init__(self, name, d, D, epsilon_r, sigma, se_db):
        # Entity 1 Properties
        self.name = name
        self.d = d  # inner conductor m
        self.D = D  # outer shield m
        self.gap = D - d
        self.epsilon_r = epsilon_r
        self.sigma = sigma  # Conductivity
        self.se_db = se_db  # Shielding Effectiveness in dB

class Atmosphere:
    def __init__(self, altitude_ft):
        # Entity 2 Properties
        self.altitude = altitude_ft
        # Barometric pressure formula
        self.pressure = 101.325 * np.exp(-0.0000366 * altitude_ft)