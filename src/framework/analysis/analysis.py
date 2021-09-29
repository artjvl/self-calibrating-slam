from src.framework.analysis.SimulationSet import SimulationSet
from src.framework.optimiser.Optimiser import Optimiser
from src.simulation.results.ResultsConstantBias import ResultsConstantBiasWithout, \
    ResultsConstantBiasStatic
from src.simulation.results.ResultsConstantScale import ResultsConstantScaleWithout, \
    ResultsConstantScaleStatic
from src.simulation.results.ResultsSinBias import ResultsSinBiasWithout, ResultsSinBiasTimelyBatch, \
    ResultsSinBiasSliding, \
    ResultsSinBiasSlidingOld, ResultsSinBiasStatic
from src.simulation.results.ResultsSinScale import ResultsSinScaleWithout, ResultsSinScaleStatic, \
    ResultsSinScaleTimelyBatch, ResultsSinScaleSliding, ResultsSinScaleSlidingOld

optimiser: 'Optimiser' = Optimiser()

# constant
is_manhattan_const_bias: bool = True
is_manhattan_const_scale: bool = True
is_intel_const_bias: bool = True
is_intel_const_scale: bool = True

# dynamic
is_manhattan_sin_bias: bool = True
is_manhattan_sin_scale: bool = True
is_intel_sin_bias: bool = True
is_intel_sin_scale: bool = True

sim_set = SimulationSet()

# CONSTANT: MANHATTAN
if is_manhattan_const_bias:
    sim_set.add(
        'manhattan_constant-bias_without',
        ResultsConstantBiasWithout(optimiser=optimiser).set_manhattan().set_steps(200),
        [1, 2, 3, 4, 5, 6, 7],
        20
    )
    sim_set.add(
        'manhattan_constant-bias_static',
        ResultsConstantBiasStatic(optimiser=optimiser).set_manhattan().set_steps(200),
        [1, 2, 3, 4, 5, 6, 7],
        3
    )

if is_manhattan_const_scale:
    sim_set.add(
        'manhattan_constant-scale_without',
        ResultsConstantScaleWithout(optimiser=optimiser).set_manhattan().set_steps(200),
        [1, 2, 3, 4, 5, 6, 7],
        20
    )
    sim_set.add(
        'manhattan_constant-scale_static',
        ResultsConstantScaleStatic(optimiser=optimiser).set_manhattan().set_steps(200),
        [1, 2, 3, 4, 5, 6, 7],
        3
    )


# CONSTANT: INTEL
if is_intel_const_bias:
    sim_set.add(
        'intel_constant-bias_without',
        ResultsConstantBiasWithout(optimiser=optimiser).set_intel().set_steps(300),
        [1, 2, 3, 4, 5, 6, 7],
        20
    )
    sim_set.add(
        'intel_constant-bias_static',
        ResultsConstantBiasStatic(optimiser=optimiser).set_intel().set_steps(300),
        [1, 2, 3, 4, 5, 6, 7],
        3
    )

if is_intel_const_scale:
    sim_set.add(
        'intel_constant-scale_without',
        ResultsConstantScaleWithout(optimiser=optimiser).set_intel().set_steps(300),
        [1, 2, 3, 4, 5, 6, 7],
        10
    )
    sim_set.add(
        'intel_constant-scale_static',
        ResultsConstantScaleStatic(optimiser=optimiser).set_intel().set_steps(300),
        [1, 2, 3, 4, 5, 6, 7],
        3
    )

# SIN: MANHATTAN
if is_manhattan_sin_bias:
    sim_set.add(
        'manhattan_sin-bias_without',
        ResultsSinBiasWithout(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-bias_static',
        ResultsSinBiasStatic(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-bias_timelybatch',
        ResultsSinBiasTimelyBatch(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-bias_dynamicsliding',
        ResultsSinBiasSliding(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-bias_sliding',
        ResultsSinBiasSlidingOld(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )

if is_manhattan_sin_scale:
    sim_set.add(
        'manhattan_sin-scale_without',
        ResultsSinScaleWithout(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-scale_static',
        ResultsSinScaleStatic(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-scale_timelybatch',
        ResultsSinScaleTimelyBatch(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-scale_dynamicsliding',
        ResultsSinScaleSliding(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )
    sim_set.add(
        'manhattan_sin-scale_sliding',
        ResultsSinScaleSlidingOld(optimiser=optimiser).set_manhattan(),
        [1, 2, 3],
        10
    )

sim_set.run()
