import typing as tp
from abc import ABC

from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2
from src.simulation.results.Results import Results

def f_step(x):
    if x > 100:
        return 0.1
    return -0.2


class ResultsConstantBias(Results, ABC):
    def loop(self, iteration: int) -> None:
        pass

    def initialise(self) -> None:
        super().initialise()

        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.truth_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.1), ParameterSpecification.BIAS, index=0
            )