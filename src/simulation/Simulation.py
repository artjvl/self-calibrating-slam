import typing as tp
from enum import Enum

from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.simulation.dataset.IntelDatasetSim import IntelDatasetSim
from src.simulation.dataset.IntelDatasetSimWith import IntelDatasetSimWith
from src.simulation.dataset.MitDatasetSimulation import MitDatasetSimulation
from src.simulation.manhattan.ManhattanSim import ManhattanSim
from src.simulation.manhattan.ManhattanSimWith import ManhattanSimWith


class Simulation(Enum):
    MANHATTAN_SIM: tp.Type[BiSimulation2D] = ManhattanSim
    MANHATTAN_SIM_WITH: tp.Type[BiSimulation2D] = ManhattanSimWith
    INTEL_SIM: tp.Type[BiSimulation2D] = IntelDatasetSim
    INTEL_SIM_WITH: tp.Type[BiSimulation2D] = IntelDatasetSimWith
    MIT: tp.Type[BiSimulation2D] = MitDatasetSimulation
