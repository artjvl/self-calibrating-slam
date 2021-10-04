import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.ppg.parameter.BaseParameterNode import BaseParameterNode
from src.framework.ppg.parameter.ParameterSpecification import ParameterSpecification

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector3


class ParameterNodeSE2(BaseParameterNode[SE2]):
    _type = SE2

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[SE2] = None,
            specification: ParameterSpecification = ParameterSpecification.BIAS,
            timestep: int = 0,
            index: int = 0
    ):
        super().__init__(name, id_, value, specification, timestep, index)

    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in [
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET
        ]
        super().set_specification(specification)

    def reset(self) -> None:
        self.set_zero()

    def to_vector3(self) -> 'Vector3':
        return self.to_vector()
