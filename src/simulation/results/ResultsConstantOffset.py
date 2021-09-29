import typing as tp
from abc import ABC

from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2
from src.simulation.results.Results import Results


class ResultsConstantOffset(Results, ABC):
    def initialise(self) -> None:
        super().initialise()

        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.1), ParameterSpecification.OFFSET, index=0
            )
        elif config == 2:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.1), ParameterSpecification.OFFSET, index=1
            )
        elif config == 3:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.15), ParameterSpecification.OFFSET, index=2
            )
        elif config == 4:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0.1, 0.1), ParameterSpecification.OFFSET, index=2
            )
        elif config == 5:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0.1, 0.15), ParameterSpecification.OFFSET, index=1
            )
        elif config == 6:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0.1, 0.15), ParameterSpecification.OFFSET, index=0
            )
        elif config == 7:
            self.truth_simulation().add_static_parameter(
                'wheel', 'offset',
                SE2.from_translation_angle_elements(0.1, 0.1, 0.15), ParameterSpecification.OFFSET
            )

    def loop(self, iteration: int) -> None:
        pass

    def finalise(self) -> None:
        pass


class ResultsConstantOffsetWithout(ResultsConstantOffset):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()


class ResultsConstantOffsetStatic(ResultsConstantOffset):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()

    def initialise(self) -> None:
        super().initialise()
        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.), ParameterSpecification.OFFSET, index=0
            )
        elif config == 2:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.), ParameterSpecification.OFFSET, index=1
            )
        elif config == 3:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector1(0.), ParameterSpecification.OFFSET, index=2
            )
        elif config == 4:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0., 0.), ParameterSpecification.OFFSET, index=2
            )
        elif config == 5:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0., 0.), ParameterSpecification.OFFSET, index=1
            )
        elif config == 6:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                Vector2(0., 0.), ParameterSpecification.OFFSET, index=0
            )
        elif config == 7:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'offset',
                SE2.from_translation_angle_elements(0., 0., 0.), ParameterSpecification.OFFSET
            )
