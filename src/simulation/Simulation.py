import typing as tp
from enum import Enum

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.simulation.calibration.ReturnTripSim import ReturnTripSim
from src.simulation.calibration.SingleTripSim import SingleTripSim
from src.simulation.calibration.SquarePriorTripSim import SquarePriorTripSim
from src.simulation.manhattan.ManhattanSim import ManhattanSim
from src.simulation.tutorial_slam2d.TutorialSimulation import TutorialSimulation


class Simulation(Enum):
    MANHATTAN: tp.Type[BiSimulation2D] = ManhattanSim
    SQUARE_TRIP: tp.Type[BiSimulation2D] = SquarePriorTripSim
    SINGLE_TRIP: tp.Type[BiSimulation2D] = SingleTripSim
    RETURN_TRIP: tp.Type[BiSimulation2D] = ReturnTripSim
    TUTORIAL_SLAM2D: tp.Type[BiSimulation2D] = TutorialSimulation
