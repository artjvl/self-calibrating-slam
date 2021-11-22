import typing as tp
from abc import ABC

from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2
from src.simulation.results.Results import Results

Parameter = tp.Union[Vector1, Vector2, SE2]


def parse_config(
        pars: tp.List[tp.Optional[float]],
        init: tp.Optional[float] = None
) -> tp.Tuple[Parameter, int]:
    assert len(pars) == 3
    num_none: int = pars.count(None)
    if init is not None:
        pars = [init if par is not None else None for par in pars]
    pars_not_none: tp.List[float] = [par for par in pars if par is not None]

    if num_none == 0:
        return SE2.from_translation_angle_elements(*pars), 0
    elif num_none == 1:
        return Vector2(pars_not_none), pars.index(None)
    return Vector1(pars_not_none), pars.index(pars_not_none[0])


class ResultsConstantOffset(Results, ABC):
    def initialise(self) -> None:
        super().initialise()

        config: tp.List[float] = self.get_config()
        assert isinstance(config, list)
        value, index = parse_config(config)
        self.truth_simulation().add_static_parameter(
            'wheel', 'offset',
            value, ParameterSpecification.OFFSET, index=index
        )

    def loop(self, iteration: int) -> None:
        pass

    def finalise(self) -> None:
        pass


class ResultsConstantOffsetWithout(ResultsConstantOffset):
    def configure(self) -> None:
        super().configure()
        self.set_optimising_simulation()


class ResultsConstantOffsetStatic(ResultsConstantOffsetWithout):
    def initialise(self) -> None:
        super().initialise()

        config: tp.List[float] = self.get_config()
        assert isinstance(config, list)
        value, index = parse_config(config, 0.)
        self.estimate_simulation().add_static_parameter(
            'wheel', 'offset',
            value, ParameterSpecification.OFFSET, index=index
        )
