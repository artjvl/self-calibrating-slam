from src.simulation.results.ResultsConstantScale import ResultsConstantScaleWithout, ResultsConstantScaleStatic
from src.framework.analysis.sim.SimulationSet import SimulationSet
from src.framework.optimiser.Optimiser import Optimiser
from src.simulation.results.ResultsConstantBias import ResultsConstantBiasWithout, ResultsConstantBiasStatic

optimiser: Optimiser = Optimiser()


sim_set = SimulationSet()

# Manhattan constant bias
sim_set.add(
    'intel_constant-bias_without',
    ResultsConstantBiasWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    10, [
        [0., 0., 0.],
        [0.1, None, None],
        [None, 0.1, None],
        [None, None, 0.1],
        [0.1, 0.1, None],
        [0.1, None, 0.1],
        [None, 0.1, 0.1],
        [0.1, 0.1, 0.1]
    ]
)
sim_set.add(
    'intel_constant-bias_static',
    ResultsConstantBiasStatic(optimiser=optimiser).set_manhattan().set_steps(200),
    10, [
        [0., 0., 0.],
        [0.1, None, None],
        [None, 0.1, None],
        [None, None, 0.1],
        [0.1, 0.1, None],
        [0.1, None, 0.1],
        [None, 0.1, 0.1],
        [0.1, 0.1, 0.1]
    ]
)

# Manhattan constant scale
sim_set.add(
    'manhattan_constant-scale_without',
    ResultsConstantScaleWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    10, [
        [1., None, 1.],
        [1.1, None, None],
        [None, None, 1.1],
        [1.1, None, 1.1]
    ]
)
sim_set.add(
    'manhattan_constant-scale_static',
    ResultsConstantScaleStatic(optimiser=optimiser).set_manhattan().set_steps(200),
    10, [
        [1., None, 1.],
        [1.1, None, None],
        [None, None, 1.1],
        [1.1, None, 1.1]
    ]
)

sim_set.run()