import typing as tp

from src.framework.simulation.simulations.ManhattanSimulation2D import ManhattanSimulation2D
from src.simulation.calibration.ReturnTripSim import ReturnTripSim
from src.simulation.calibration.SingleTripSim import SingleTripSim
from src.simulation.dataset.IntelDatasetSim import IntelDatasetSim, IntelDatasetSimWithConstant, \
    IntelDatasetSimWithSliding, IntelDatasetSimWithOldSliding
from src.simulation.dataset.MitDatasetSimulation import MitDatasetSimulation
from src.simulation.manhattan.ManhattanSim import ManhattanSim, ManhattanSimWithConstant, ManhattanSimWithSliding
from src.simulation.manhattan.ManhattanSimTest import ManhattanSimTest

SimType = tp.Type['SubSimulation2D']


class SimulationList(object):
    _simulations: tp.Dict[str, tp.List[SimType]]

    def __init__(self):
        self._simulations = {}

    def sections(self) -> tp.List[str]:
        return list(self._simulations.keys())

    def add(
            self,
            section: str,
            simulation: SimType
    ):
        if section not in self._simulations:
            self._simulations[section] = []
        self._simulations[section].append(simulation)

    def list(
            self,
            section: str
    ) -> tp.List[SimType]:
        assert section in self._simulations
        return self._simulations[section]


simulations = SimulationList()

manhattan_section: str = ManhattanSimulation2D.__name__
simulations.add(manhattan_section, ManhattanSim)
simulations.add(manhattan_section, ManhattanSimWithConstant)
simulations.add(manhattan_section, ManhattanSimWithSliding)
simulations.add(manhattan_section, ManhattanSimTest)

intel_section: str = 'Intel'
simulations.add(intel_section, IntelDatasetSim)
simulations.add(intel_section, IntelDatasetSimWithConstant)
simulations.add(intel_section, IntelDatasetSimWithSliding)
simulations.add(intel_section, IntelDatasetSimWithOldSliding)

mit_section: str = 'MIT'
simulations.add(mit_section, MitDatasetSimulation)

other_section: str = 'Other'
simulations.add(other_section, SingleTripSim)
simulations.add(other_section, ReturnTripSim)
