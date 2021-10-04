import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.graph.parameter.BaseParameterNode import BaseParameterNode
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector3


class ParameterNodeSE2(BaseParameterNode[SE2]):
    _type = SE2

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[SE2] = None,
            specification: ParameterSpecification = None,
            id_: int = 0,
            timestep: int = 0,
            index: int = 0
    ):
        if specification is None:
            specification = ParameterSpecification.BIAS
        super().__init__(
            name,
            value=value, specification=specification, id_=id_, timestep=timestep, index=index
        )

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
