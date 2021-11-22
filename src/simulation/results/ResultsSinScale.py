from abc import ABC

import numpy as np
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
from src.framework.math.matrix.vector import Vector1
from src.simulation.results.Results import Results


def f_sin(
        x: float,
        factor: int = 1
) -> float:
    return 1. + 0.1 * np.sin(factor * 2 * np.pi * x / 200.)


class ResultsSinScale(Results, ABC):
    def initialise(self) -> None:
        super().initialise()
        self.truth_simulation().add_static_parameter(
            'wheel', 'scale',
            Vector1.ones(), ParameterSpecification.SCALE
        )

    def loop(self, iteration: int) -> None:
        self.truth_simulation().update_parameter(
            'wheel', 'scale',
            Vector1(
                f_sin(iteration, 2)
            )
        )

    def finalise(self) -> None:
        pass


class ResultsSinScaleWithout(ResultsSinScale):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()


class ResultsSinScaleStatic(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()

        self.estimate_simulation().add_static_parameter(
            'wheel', 'scale',
            Vector1.ones(), ParameterSpecification.SCALE
        )


class ResultsSinScaleTimelyBatch(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_timely_parameter(
            'wheel', 'scale',
            Vector1.ones(), ParameterSpecification.SCALE, config
        )


class ResultsSinScaleSliding(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_sliding_parameter(
            'wheel', 'scale',
            Vector1.ones(), ParameterSpecification.SCALE, config
        )


class ResultsSinScaleSlidingOld(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()

        config: int = self.get_config()
        assert isinstance(config, int)
        self.estimate_simulation().add_old_sliding_parameter(
            'wheel', 'scale',
            Vector1.ones(), ParameterSpecification.SCALE, config
        )
