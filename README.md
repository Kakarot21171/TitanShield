# TitanShield
TitanShield is a physics-based RF cable simulation platform that models coaxial performance under extreme aerospace conditions. It analyzes atmospheric breakdown voltage, shielding effectiveness, and phase shift from thermal and high-G loads. Built with FastAPI and React, it provides real-time interactive visualization of mission scenarios.

# Project Status 
* Modular simulation architecture (src/)
* Paschen’s Law altitude-based dielectric breakdown model
* Shielding effectiveness / EMI ingress model
* Mission success/failure evaluation logic
* Basic GUI interface (Tkinter)
* Matplotlib-based visualization module
* Git-based version control and clean repository structure
* UML class and sequence diagrams

# In Progress/ To Be Implemented
* Temperature-dependent dielectric constant model=
* Phase error (degrees) calculation
* Frequency-dependent shielding model
* Maximum safe power (wattage) computation
* CSV export of mission results
* Additional validation testing

# Changes from Original Proposal
* Consolidated duplicate CoaxLine implementations into a single modular design.
* Refactored project into a src/ structure for cleaner separation of source and environment.
* Removed packaged executable builds from version control to follow best practices.

# Installation Instructions
Requirements
* Python 3.10+ (tested with Python 3.11)
* pip
* Git (optional)
* Core Dependencies
* numpy
* matplotlib
* tkinter (included with standard Python installation)

# Step-by-Step Setup
1. Clone the repository
   * git clone https://github.com/Kakarot21171/TitanShield/blob/main/requirements.txt
   * cd TitanShield
2. Create a virtual environment
   * python -m venv .venv
3. Activate the virtual environment
   * Windows
     * .\.venv\Scripts\Activate.ps1
   * Mac/Linux
     * source .venv/bin/activate
4. Install dependencies
   * pip install -r requirements.txt

# Troubleshooting
* "ModuleNotFoundError"
    * Make sure the virtual environment is activated and dependencies are installed:
      * pip install -r requirements.txt
* PowerShell won’t activate venv
  * If activation is blocked:
    * Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Usage
* Run the Simulation(CLI)
  * From the project root:
    * python src/main.py
      * This executes the mission simulation using default altitude, voltage, and interference parameters defined in the script.
* Run the GUI Version
  * python src/app.py
    * The GUI allows interactive adjustment of:
    * Altitude 
    * Cable selection 
    * Mission check execution
* Expected Output
  * The simulation outputs: 
    * The simulation outputs:
    * Breakdown voltage threshold 
    * Noise ingress level 
    * Mission status (SUCCESS / FAILED)
    * Visual altitude vs breakdown voltage graph (if using visualizer)
    * Failure states include:
    * Arc-over due to dielectric breakdown 
    * Mission failure due to EMI leakage

# Architecture Overview 
* TitanShield follows a modular architecture separating:
  1. Entities (entities.py)
     * Defines physical system components:
       * CoaxLine (cable properties)
       * Atmosphere (pressure vs altitude)
  2. Models (models.py)
     * Contains mathematical algorithms:
       * Paschen breakdown voltage calculation 
       * Shielding leakage model 
       * Attenuation modeling
  3. Simulation Core (main.py)
     * Orchestrates:
        * Entity instantiation
        * Model interaction
        * Failure-state evaluation
        * Data output
  4.  GUI Interface (app.py)
     * Provides interactive front-end control for mission simulation.
  5. Visualization (visualizer.py)
     * Generates altitude-risk analysis graphs using Matplotlib.
* UML Mapping
  * The UML class diagram maps directly to:
    * Entity classes (CoaxLine, Atmosphere)
    * Model functions (computational modules)
    * Simulation orchestrator (main)
    * User interface layer (app)
    * Sequence diagrams represent:
      * Mission simulation execution flow 
      * GUI-triggered model evaluation 
* Architectural Changes 
  * Refactored duplicate class definitions into cleaner modular separation. 
  * Moved all source code into src/ for clarity. 
  * Separated build artifacts and virtual environments from repository tracking. 
  * Improved separation of concerns between UI, models, and entities.


