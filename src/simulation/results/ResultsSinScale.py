import typing as tp
from abc import ABC

import numpy as np
from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.matrix.vector import Vector1
from src.simulation.results.Results import Results


def f_sin(
        x: float,
        factor: int = 0
) -> float:
    factor += 1
    return 1. + 0.1 * np.sin(factor * 2 * np.pi * x / 200.)


class ResultsSinScale(Results, ABC):
    def initialise(self) -> None:
        super().initialise()

        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=0
            )
        elif config == 2:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=1
            )
        elif config == 3:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=2
            )

    def loop(self, iteration: int) -> None:
        self.truth_simulation().update_parameter('wheel', 'scale', Vector1(f_sin(iteration)))

    def finalise(self) -> None:
        pass


class ResultsSinScaleWithout(ResultsSinScale):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()

class ResultsSinScaleStatic(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, index=2
            )


class ResultsSinScaleTimelyBatch(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=2
            )


class ResultsSinScaleSliding(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=2
            )


class ResultsSinScaleSlidingOld(ResultsSinScaleWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'scale',
                Vector1(1.), ParameterSpecification.SCALE, 20, index=2
            )
