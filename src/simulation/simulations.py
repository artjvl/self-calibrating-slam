import typing as tp

from src.framework.simulation.Simulation import SubSimulationManager
from src.simulation.dataset.IntelDatasetSim import intel_sim_plain, intel_sim_inc, intel_sim_sliding, \
    intel_sim_old_sliding
from src.simulation.manhattan.ManTestSim import manhattan_test_post
from src.simulation.manhattan.ManhattanSim import manhattan_sim_plain, manhattan_sim_inc, manhattan_sim_sliding


class SimulationList(object):
    _simulations: tp.Dict[str, tp.List['SubSimulationManager']]

    def __init__(self):
        self._simulations = {}

    def sections(self) -> tp.List[str]:
        return list(self._simulations.keys())

    def add(
            self,
            section: str,
            simulation: 'SubSimulationManager'
    ):
        if section not in self._simulations:
            self._simulations[section] = []
        self._simulations[section].append(simulation)

    def simulations(
            self,
            section: str
    ) -> tp.List['SubSimulationManager']:
        assert section in self._simulations
        return self._simulations[section]


simulations = SimulationList()

section: str = 'ManhattanSim'
simulations.add(section, manhattan_sim_plain)
simulations.add(section, manhattan_sim_inc)
simulations.add(section, manhattan_sim_sliding)

section = 'ManhattanTest'
simulations.add(section, manhattan_test_post)

section = 'IntelSim'
simulations.add(section, intel_sim_plain)
simulations.add(section, intel_sim_inc)
simulations.add(section, intel_sim_sliding)
simulations.add(section, intel_sim_old_sliding)
