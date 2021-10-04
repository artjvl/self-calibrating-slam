import typing as tp

from src.framework.math.matrix.vector import Vector3
from src.framework.ppg.parameter.BaseParameterNode import BaseParameterNode
from src.framework.ppg.parameter.ParameterSpecification import ParameterSpecification


class ParameterNodeV3(BaseParameterNode[Vector3]):
    _type = Vector3

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[Vector3] = None,
            specification: ParameterSpecification = ParameterSpecification.SCALE,
            timestep: int = 0,
            index: int = 0
    ):
        super().__init__(name, id_, value, specification, timestep, index)

    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in [
            ParameterSpecification.SCALE
        ]
        super().set_specification(specification)

    def reset(self) -> None:
        filler: float = 0.
        if self.get_specification() == ParameterSpecification.SCALE:
            filler = 1.
        list_: tp.List[float] = [filler for _ in range(3)]
        self.set_value(Vector3(list_))

    def to_vector3(self) -> Vector3:
        return self.get_value()
