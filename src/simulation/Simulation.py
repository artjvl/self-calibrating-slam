from enum import Enum

from framework.simulation.BiSimulation2D import BiSimulation2D
from simulation.calibration.CalibrationSimulation import CalibrationSimulation
from src.simulation.hardcoded.HardcodedSimulation import HardcodedSimulation
from src.simulation.tutorial_slam2d.TutorialSimulation import TutorialSimulation


class Simulation(Enum):
    CALIBRATION: BiSimulation2D = CalibrationSimulation()
    HARDCODED: BiSimulation2D = HardcodedSimulation()
    TUTORIAL_SLAM2D: BiSimulation2D = TutorialSimulation()
