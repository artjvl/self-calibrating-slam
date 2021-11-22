import typing as tp

from src.simulation.results.ResultsSinScale import ResultsSinScaleTimelyBatch
from src.simulation.results.ResultsSpatialBias1D import ResultsSpatialBias1DSpatial
from src.simulation.results.ResultsSpatialBias import ResultsSpatialBiasSpatial, ResultsSpatialBiasWithout
from src.simulation.dataset.IntelDatasetSim import IntelPlain, IntelSliding, IntelSlidingOld, \
    IntelWithout, IntelConstant, IntelTimely, IntelSpatial
from src.simulation.manhattan.ManhattanSim import ManhattanPlain, ManhattanConstant, ManhattanSliding, \
    ManhattanWithout, ManhattanTimely, ManhattanSlidingOld, ManhattanSpatial
from src.simulation.results.ResultsConstantBias import ResultsConstantBiasWithout, ResultsConstantBiasStatic
from src.simulation.results.ResultsConstantScale import ResultsConstantScaleWithout, ResultsConstantScaleStatic
from src.simulation.results.ResultsPlain import ResultsPlain
from src.simulation.results.ResultsSinBias import ResultsSinBiasWithout, ResultsSinBiasTimelyBatch, \
    ResultsSinBiasSliding, ResultsSinBiasSlidingOld

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
            simulation: 'SubBiSimulation',
            name: tp.Optional[str] = None
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

section: str = 'Demo'
simulations.add(section, ResultsConstantBiasWithout().set_intel().set_steps(200).set_config([None, None, 0.1]).set_name('Demo: Intel y-bias (PGO)'))
simulations.add(section, ResultsConstantBiasStatic().set_intel().set_steps(200).set_config([None, None, 0.1]).set_name('Demo: Intel y-bias (PPGO)'))
simulations.add(section, ResultsSinBiasSliding().set_intel().set_steps(200).set_config(5).set_name('Demo: Intel sin xyz-bias (PPGO)'))
simulations.add(section, ResultsSinBiasSliding().set_manhattan().set_steps(200).set_config(5).set_name('Demo: Manhattan sin xyz-bias (PPGO)'))
# simulations.add(section, ResultsConstantScaleWithout().set_manhattan().set_steps(100).set_config([1.1, None, 1.1]))
# simulations.add(section, ResultsSinBiasTimelyBatch().set_manhattan().set_steps(200).set_config(10))
# simulations.add(section, ResultsSpatialBiasWithout().set_manhattan().set_steps(400))
# simulations.add(section, ResultsSpatialBiasSpatial().set_intel().set_steps(800))

simulations.add(section, ResultsPlain().set_manhattan().set_steps(200).set_name('ResultsPlain-Manhattan'))
simulations.add(section, ResultsPlain().set_intel().set_steps(300).set_name('ResultsPlain-Intel'))
simulations.add(section, ResultsConstantBiasWithout().set_intel().set_steps(300).set_name('ResultsConstantBiasWithout-Intel'))
simulations.add(section, ResultsConstantBiasStatic().set_intel().set_steps(300).set_name('ResultsConstantBiasStatic-Intel'))
simulations.add(section, ResultsConstantBiasWithout().set_manhattan().set_steps(200).set_name('ResultsConstantBiasWithout-Manhattan'))
simulations.add(section, ResultsConstantBiasStatic().set_manhattan().set_steps(200).set_name('ResultsConstantBiasStatic-Manhattan'))
simulations.add(section, ResultsConstantScaleWithout().set_intel().set_steps(300).set_name('ResultsConstantScaleWithout-Intel'))
simulations.add(section, ResultsConstantScaleStatic().set_intel().set_steps(300).set_name('ResultsConstantScaleStatic-Intel'))
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
