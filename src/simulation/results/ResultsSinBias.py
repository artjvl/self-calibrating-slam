from abc import ABC

import numpy as np
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.simulation.results.Results import Results


def f_sin(
        x: float,
        factor: int = 1
) -> float:
    return 0.1 * np.sin(factor * 2 * np.pi * x / 200.)


class ResultsSinBias(Results, ABC):
    def initialise(self) -> None:
        super().initialise()
        self.truth_simulation().add_static_parameter(
            'wheel', 'bias',
            SE2.from_zeros(), ParameterSpecification.BIAS
        )

    def loop(self, iteration: int) -> None:
        self.truth_simulation().update_parameter(
            'wheel', 'bias',
            SE2.from_translation_angle_elements(
                f_sin(iteration, 1),
                f_sin(iteration, 2),
                f_sin(iteration, 3),
            )
        )

    def finalise(self) -> None:
        pass


class ResultsSinBiasWithout(ResultsSinBias):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()


class ResultsSinBiasStatic(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()

        self.estimate_simulation().add_static_parameter(
            'wheel', 'bias',
            SE2.from_zeros(), ParameterSpecification.BIAS
        )


class ResultsSinBiasTimelyBatch(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_timely_parameter(
            'wheel', 'bias',
            SE2.from_zeros(), ParameterSpecification.BIAS, config
        )


class ResultsSinBiasSliding(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_sliding_parameter(
            'wheel', 'bias',
            SE2.from_zeros(), ParameterSpecification.BIAS, config
        )


class ResultsSinBiasSlidingOld(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_old_sliding_parameter(
            'wheel', 'bias',
            SE2.from_zeros(), ParameterSpecification.BIAS, config
        )
