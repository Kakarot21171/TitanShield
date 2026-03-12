# TitanShield

TitanShield is a modeling and simulation tool designed to analyze RF phase shift behavior in coaxial cables under varying environmental and mechanical conditions.

The simulator allows engineers and students to explore how frequency, temperature changes, gravitational loading, cable sag, and cable length influence signal phase propagation in common coaxial transmission lines.

TitanShield combines physics-based simulation models, interactive visualization, and automated batch simulation to create an engineering-focused analysis tool.

# Project Status

* Modular simulation architecture
* RF phase shift simulation model
* Cable library with RG-58, RG-213, and LMR-400
* Mechanical sag modeling for cable length variation
* Temperature-dependent electrical length modeling
* Interactive GUI interface (Tkinter)
* Matplotlib-based visualization module
* Batch simulation runner with JSON configuration
* CSV export of simulation results
* Basic verification tests

# In Progress / To Be Implemented

* Temperature-dependent dielectric constant model
* Phase error (degrees) calculation
* Frequency-dependent shielding model
* Impedance mismatch modeling
* Maximum safe power computation
* Continuous phase unwrapping for plots
* Expanded validation and testing framework

# Changes from Original Proposal

* Refactored the project into modular components separating GUI, models, visualization, and entities.
* Added automated batch simulation capability using a JSON run configuration.
* Implemented cable sag modeling to simulate mechanical effects on electrical length.
* Added CSV export functionality for simulation data analysis.
* Improved separation of concerns between user interface and physics models.

# Installation Instructions

Requirements

* Python 3.9+
* pip
* Git (optional)

Core Dependencies

* numpy
* matplotlib
* tkinter (included with standard Python installations)

# Step-by-Step Setup

1. Clone the repository

* git clone https://github.com/yourusername/TitanShield.git
* cd TitanShield

2. Create a virtual environment

* python -m venv .venv

3. Activate the virtual environment

Windows
* .\.venv\Scripts\Activate.ps1

Mac/Linux
* source .venv/bin/activate

4. Install dependencies

* pip install numpy matplotlib

# Troubleshooting

* "ModuleNotFoundError"

  * Make sure the virtual environment is activated and dependencies are installed:
  * pip install numpy matplotlib

* PowerShell won’t activate the virtual environment

  * If activation is blocked:
  * Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Usage

* Run the GUI Simulator

  * From the project root:

  * python main.py

  * This launches the TitanShield graphical interface.

* Run Batch Simulations

  * python runner.py

  * Batch runs are configured in:

  * run_plan.json

# Expected Output

Simulation runs generate:

* Phase shift vs frequency plot
* CSV file containing frequency and phase shift data
* JSON summary containing simulation statistics

Example output files:

* runs/run_001_timeseries.csv
* runs/run_001_summary.json

# Simulation Models

TitanShield models several physical effects that influence RF signal propagation.

Transmission Line Phase Model

* Phase (degrees) = 360 × (Electrical Length / Wavelength)

Where:

* Electrical Length = cable length adjusted by environmental effects
* Wavelength = propagation velocity / frequency

Temperature Effects

* L_effective = L × (1 + α × ΔT)

Where:

* L = cable length
* α = cable temperature coefficient
* ΔT = temperature change

Mechanical Sag Effects

The additional cable length caused by sag is estimated using a small-sag approximation:

* ΔL ≈ (8s²) / (3D)

Where:

* s = sag height
* D = clamp spacing

# Architecture Overview

TitanShield follows a modular architecture separating simulation logic, visualization, and user interface components.

1. Entities (entities.py)

* Defines cable properties and system parameters
* Cable velocity factor
* Temperature coefficient
* Attenuation properties

2. Models (models.py)

* Contains the physics-based algorithms used in the simulation
* Phase shift computation
* Frequency sweep generation
* Environmental parameter effects

3. Simulation Runner (runner.py)

* Handles automated simulation execution
* Loads simulation configurations
* Runs frequency sweeps
* Exports results to CSV and JSON

4. GUI Interface (app.py)

* Provides interactive simulation controls
* Parameter sliders
* Cable selection
* Simulation recomputation
* Status reporting

5. Visualization (visualizer.py)

* Generates simulation plots using Matplotlib
* Phase vs frequency graph
* Dynamic GUI updates

# Verification

Basic verification tests are included to confirm correct baseline model behavior.

* Run tests with:

* python verify.py

These tests confirm that baseline conditions produce expected simulation outputs.

# Educational Purpose

TitanShield was developed as part of a modeling and simulation engineering project demonstrating how environmental and mechanical conditions affect RF signal propagation in coaxial cables.

The project emphasizes:

* physics-based simulation modeling
* modular software architecture
* interactive visualization
* experiment automation
* engineering analysis of RF transmission systems

# License

This project is intended for educational and research use.
