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
    return 0.1 * np.sin(factor * 2 * np.pi * x / 200.)


class ResultsSinBias(Results, ABC):
    def initialise(self) -> None:
        super().initialise()

        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.truth_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=0
            )
        elif config == 2:
            self.truth_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=1
            )
        elif config == 3:
            self.truth_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=2
            )

    def loop(self, iteration: int) -> None:
        self.truth_simulation().update_parameter('wheel', 'bias', Vector1(f_sin(iteration)))

    def finalise(self) -> None:
        pass


class ResultsSinBiasWithout(ResultsSinBias):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()

class ResultsSinBiasStatic(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, index=2
            )


class ResultsSinBiasTimelyBatch(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_timely_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=2
            )


class ResultsSinBiasSliding(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=2
            )


class ResultsSinBiasSlidingOld(ResultsSinBiasWithout):
    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_old_sliding_parameter(
                'wheel', 'bias',
                Vector1(0.), ParameterSpecification.BIAS, 20, index=2
            )
