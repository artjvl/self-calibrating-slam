from src.framework.analysis.sim.SimulationSet import SimulationSet
from src.framework.optimiser.Optimiser import Optimiser
from src.simulation.results.ResultsConstantBias import ResultsConstantBiasWithout, ResultsConstantBiasStatic
from src.simulation.results.ResultsConstantScale import ResultsConstantScaleStatic, ResultsConstantScaleWithout

optimiser: Optimiser = Optimiser()

sim_set = SimulationSet()

# Manhattan constant bias (0.0, 0.0, 0.0)
sim_set.add(
    'manhattan_constant-bias-0.0_without',
    ResultsConstantBiasWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[0., 0., 0.]]
)
sim_set.add(
    'manhattan_constant-bias-0.0_static',
    ResultsConstantBiasStatic(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[0., 0., 0.]]
)

# Manhattan constant bias (0.1, 0.1, 0.1)
sim_set.add(
    'manhattan_constant-bias-0.1_without',
    ResultsConstantBiasWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[0.1, 0.1, 0.1]]
)
sim_set.add(
    'manhattan_constant-bias-0.1_static',
    ResultsConstantBiasStatic(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[0.1, 0.1, 0.1]]
)

# Manhattan constant scale (0.1, -, 0.1)
sim_set.add(
    'manhattan_constant-scale-xy-1.1_without',
    ResultsConstantScaleWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[1.1, None, 1.1]]
)
sim_set.add(
    'manhattan_constant-scale-xy-1.1_static',
    ResultsConstantScaleStatic(optimiser=optimiser).set_manhattan().set_steps(200),
    4, [[1.1, None, 1.1]]
)

sim_set.run()
