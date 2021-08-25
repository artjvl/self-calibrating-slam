import typing as tp
from enum import Enum

from framework.simulation.Simulation2D import SubSimulation2D
from src.framework.simulation.BiSimulation2D import BiSimulation2D
from src.simulation.calibration.ReturnTripSim import ReturnTripSim
from src.simulation.calibration.SingleTripSim import SingleTripSim
from src.simulation.dataset.IntelDatasetSim import IntelDatasetSim, IntelDatasetSimWithConstant, \
    IntelDatasetSimWithSliding, IntelDatasetSimWithOldSliding
from src.simulation.dataset.MitDatasetSimulation import MitDatasetSimulation
from src.simulation.manhattan.ManhattanSim import ManhattanSim, ManhattanSimWithConstant, ManhattanSimWithSliding
from src.simulation.manhattan.ManhattanSimTest import ManhattanSimTest


class SimulationList(object):
    _simulations: tp.List[tp.Type['SubSimulation2D']]

    def add(self, simulation: tp.Type['SubSimulation2D']):
        self._simulations.append(simulation)

    def list(self) -> tp.List[tp.Type['SubSimulation2D']]:
        return self._simulations


simulations = SimulationList()

simulations.add(ManhattanSim)


class Simulation(Enum):
    MANHATTAN_SIM: tp.Type[BiSimulation2D] = ManhattanSim
    MANHATTAN_SIM_CONSTANT: tp.Type[BiSimulation2D] = ManhattanSimWithConstant
    MANHATTAN_SIM_SLIDING: tp.Type[BiSimulation2D] = ManhattanSimWithSliding
    MANHATTAN_SIM_TEST: tp.Type[BiSimulation2D] = ManhattanSimTest
    INTEL_SIM: tp.Type[BiSimulation2D] = IntelDatasetSim
    INTEL_SIM_CONSTANT: tp.Type[BiSimulation2D] = IntelDatasetSimWithConstant
    INTEL_SIM_SLIDING: tp.Type[BiSimulation2D] = IntelDatasetSimWithSliding
    INTEL_SIM_OLD_SLIDING: tp.Type[BiSimulation2D] = IntelDatasetSimWithOldSliding
    MIT: tp.Type[BiSimulation2D] = MitDatasetSimulation
    SINGLE_TRIP: tp.Type[BiSimulation2D] = SingleTripSim
    RETURN_TRIP: tp.Type[BiSimulation2D] = ReturnTripSim
