from src.framework.analysis.sim.SimulationSet import SimulationSet
from src.framework.optimiser.Optimiser import Optimiser
from src.simulation.results.ResultsSinBias import ResultsSinBiasSliding, ResultsSinBiasTimelyBatch, \
    ResultsSinBiasWithout

optimiser: Optimiser = Optimiser()

num_runs: int = 20
sim_set = SimulationSet()

sim_set.add(
    'manhattan_sin-bias_without',
    ResultsSinBiasWithout(optimiser=optimiser).set_manhattan().set_steps(200),
    num_runs
)
sim_set.add(
    'manhattan_sin-bias_sliding',
    ResultsSinBiasSliding(optimiser=optimiser).set_manhattan().set_steps(200),
    num_runs,
    [5],
)
sim_set.add(
    'manhattan_sin-bias_timely',
    ResultsSinBiasTimelyBatch(optimiser=optimiser).set_manhattan().set_steps(200),
    num_runs,
    [10],
)

sim_set.run()