from enum import Enum

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.simulation.calibration.ReturnTripSim import ReturnTripSim
from src.simulation.calibration.SingleTripSim import SingleTripSim
from src.simulation.calibration.SquarePriorTripSim import SquarePriorTripSim
from src.simulation.manhattan.ManhattanSim import ManhattanSim
from src.simulation.tutorial_slam2d.TutorialSimulation import TutorialSimulation


class Simulation(Enum):
    MANHATTAN: BiSimulation2D = ManhattanSim()
    SQUARE_TRIP: BiSimulation2D = SquarePriorTripSim()
    SINGLE_TRIP: BiSimulation2D = SingleTripSim()
    RETURN_TRIP: BiSimulation2D = ReturnTripSim()
    TUTORIAL_SLAM2D: BiSimulation2D = TutorialSimulation()
