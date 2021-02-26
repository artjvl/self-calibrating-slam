from enum import Enum

from src.framework.simulation.Simulation2D import Simulation2D
from src.simulation.hardcoded.HardcodedSimulation import HardcodedSimulation
from src.simulation.tutorial_slam2d.TutorialSimulation import TutorialSimulation


class Simulations(Enum):
    TUTORIAL_SLAM2D: Simulation2D = TutorialSimulation()
    HARDCODED: Simulation2D = HardcodedSimulation()
