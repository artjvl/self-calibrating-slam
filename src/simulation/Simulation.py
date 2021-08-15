import typing as tp
from enum import Enum

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.simulation.dataset.IntelDatasetSimulation import IntelDatasetSimulation
from src.simulation.dataset.MitDatasetSimulation import MitDatasetSimulation
from src.simulation.manhattan.ManhattanSim import ManhattanSim


class Simulation(Enum):
    MANHATTAN: tp.Type[BiSimulation2D] = ManhattanSim
    INTEL: tp.Type[BiSimulation2D] = IntelDatasetSimulation
    MIT: tp.Type[BiSimulation2D] = MitDatasetSimulation
