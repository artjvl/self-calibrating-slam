import typing as tp
from abc import ABC

import numpy as np
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
from src.framework.math.matrix.vector import Vector1
from src.framework.math.matrix.vector import Vector2
from src.simulation.results.Results import Results

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubParameterNode


def f_spatial(
        x: float,
        y: float,
        factor: int = 1
) -> float:
    # return 0.01 * np.sin(factor * 2 * np.pi * (x + y) / 200.)
    # return 0.1
    return 0.2 * np.cos(0.1 * (x + y))


class ResultsSpatialBias(Results, ABC):
    def initialise(self) -> None:
        super().initialise()
        node: 'SubParameterNode' = self.truth_simulation().add_static_parameter(
            'wheel', 'bias',
            Vector1.zeros(),
            # Vector2.zeros(),
            ParameterSpecification.BIAS
        )
        node.set_translation(self.get_current_pose().translation())

    def loop(self, iteration: int) -> None:
        translation: 'Vector2' = self.get_current_pose().translation()
        node: 'SubParameterNode' = self.truth_simulation().update_parameter(
            'wheel', 'bias',
            Vector1(f_spatial(translation[0], translation[1], 1))
            # SE2.from_translation_angle_elements(
            #     f_spatial(translation[0], translation[1], 1),
            #     f_spatial(translation[0], translation[1], 2),
            #     f_spatial(translation[0], translation[1], 3),
            # )
        )
        node.set_translation(translation)

    def finalise(self) -> None:
        pass


class ResultsSpatialBiasWithout(ResultsSpatialBias):
    def configure(self) -> None:
        super().configure()
        self.set_plain_simulation()


class ResultsSpatialBiasSpatial(ResultsSpatialBias):
    def configure(self) -> None:
        super().configure()
        self.set_post_simulation()

    def initialise(self) -> None:
        super().initialise()
        self.estimate_simulation().add_spatial_parameter(
            'wheel', 'bias',
            Vector1.zeros(),
            # SE2.from_zeros(),
            ParameterSpecification.BIAS, 20, index=0
        )

    def finalise(self) -> None:
        super().finalise()
        self.estimate_simulation().post_process()
