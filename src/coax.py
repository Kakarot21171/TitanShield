import numpy as np

class CoaxLine:
    def __init__(self, name, d, D, epsilon_r, tand, sigma):
        # Entity 1 Properties
        self.name = name
        self.d = d  # Inner conductor diameter (m)
        self.D = D  # Outer shield inner diameter (m)
        self.epsilon_r = epsilon_r  # Dielectric constant
        self.tand = tand  # Loss tangent (dielectric loss)
        self.sigma = sigma  # Conductivity of copper (S/m)

    # Behavior: Calculate Characteristic Impedance (Z0)
    def calculate_impedance(self):
        # core logic for wave physics
        return (60 / np.sqrt(self.epsilon_r)) * np.log(self.D / self.d)

    # Behavior: Calculate Frequency-Dependent Attenuation
    def get_loss_at_frequency(self, frequency_hz):
        # Algorithm 3: Modeling skin effect and loss
        # (Simplified example of the math driving the simulation)
        alpha_c = (1 / (self.d * self.sigma)) # Conductor loss component
        return alpha_c * np.sqrt(frequency_hz)