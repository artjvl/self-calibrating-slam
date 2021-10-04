import typing as tp

from simulation.results.ResultsConstantBias import ResultsConstantBiasWithout, ResultsConstantBiasStatic
from simulation.results.ResultsConstantScale import ResultsConstantScaleWithout, ResultsConstantScaleStatic
from simulation.results.ResultsSinBias import ResultsSinBiasWithout, ResultsSinBiasTimelyBatch, ResultsSinBiasSliding, \
    ResultsSinBiasSlidingOld
from src.simulation.dataset.IntelDatasetSim import IntelPlain, IntelSliding, IntelSlidingOld, \
    IntelWithout, IntelConstant, IntelTimely, IntelSpatial
from src.simulation.manhattan.ManhattanSim import ManhattanPlain, ManhattanConstant, ManhattanSliding, \
    ManhattanWithout, ManhattanTimely, ManhattanSlidingOld, ManhattanSpatial

if tp.TYPE_CHECKING:
    from src.framework.simulation.BiSimulation import SubBiSimulation


class SimulationList(object):
    _simulations: tp.Dict[str, tp.List['SubBiSimulation']]

    def __init__(self):
        self._simulations = {}

    def sections(self) -> tp.List[str]:
        return list(self._simulations.keys())

    def add(
            self,
            section: str,
            simulation: 'SubBiSimulation'
    ):
        if section not in self._simulations:
            self._simulations[section] = []
        self._simulations[section].append(simulation)

    def simulations(
            self,
            section: str
    ) -> tp.List['SubBiSimulation']:
        assert section in self._simulations
        return self._simulations[section]


simulations = SimulationList()

section: str = 'ManhattanSim'
simulations.add(section, ManhattanPlain())
simulations.add(section, ManhattanWithout())
simulations.add(section, ManhattanConstant())
simulations.add(section, ManhattanTimely())
simulations.add(section, ManhattanSliding())
simulations.add(section, ManhattanSlidingOld())
simulations.add(section, ManhattanSpatial())

section: str = 'Results'
simulations.add(section, ResultsConstantBiasWithout().set_intel().set_steps(200))
simulations.add(section, ResultsConstantBiasStatic().set_intel().set_steps(200))
simulations.add(section, ResultsConstantScaleWithout().set_intel().set_steps(200))
simulations.add(section, ResultsConstantScaleStatic().set_intel().set_steps(220))
simulations.add(section, ResultsSinBiasWithout().set_manhattan())
simulations.add(section, ResultsSinBiasTimelyBatch().set_manhattan())
simulations.add(section, ResultsSinBiasSliding().set_manhattan())
simulations.add(section, ResultsSinBiasSlidingOld().set_manhattan())

# section = 'ManhattanTest'
# simulations.add(section, manhattan_test_post)

section = 'IntelSim'
simulations.add(section, IntelPlain())
simulations.add(section, IntelWithout())
simulations.add(section, IntelConstant())
simulations.add(section, IntelTimely())
simulations.add(section, IntelSliding())
simulations.add(section, IntelSlidingOld())
simulations.add(section, IntelSpatial())
