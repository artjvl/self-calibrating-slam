import typing as tp
from abc import ABC

from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
from src.framework.math.matrix.vector import Vector1, Vector2
from src.framework.math.matrix.vector import Vector3
from src.simulation.results.Results import Results


class ResultsConstantScale(Results, ABC):
    def initialise(self) -> None:
        super().initialise()

        config: tp.Union[int, str] = self.get_config()
        if config == 1:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.1), ParameterSpecification.SCALE, index=0
            )
        elif config == 2:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.1), ParameterSpecification.SCALE, index=1
            )
        elif config == 3:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector1(1.1), ParameterSpecification.SCALE, index=2
            )
        elif config == 4:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1.1, 1.1), ParameterSpecification.SCALE, index=2
            )
        elif config == 5:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1.1, 1.15), ParameterSpecification.SCALE, index=1
            )
        elif config == 6:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1.1, 1.1), ParameterSpecification.SCALE, index=0
            )
        elif config == 7:
            self.truth_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector3(1.1, 1.1, 1.1), ParameterSpecification.SCALE
            )

    def loop(self, iteration: int) -> None:
        pass

    def finalise(self) -> None:
        pass


class ResultsConstantScaleWithout(ResultsConstantScale):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()


class ResultsConstantScaleStatic(ResultsConstantScale):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()

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
        elif config == 4:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1., 1.), ParameterSpecification.SCALE, index=2
            )
        elif config == 5:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1., 1.), ParameterSpecification.SCALE, index=1
            )
        elif config == 6:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector2(1., 1.), ParameterSpecification.SCALE, index=0
            )
        elif config == 7:
            self.estimate_simulation().add_static_parameter(
                'wheel', 'scale',
                Vector3(1., 1., 1.), ParameterSpecification.SCALE
            )
