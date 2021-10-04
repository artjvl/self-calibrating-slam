import typing as tp

from src.framework.math.matrix.vector import Vector1, Vector3
from src.framework.graph.parameter.BaseParameterNode import BaseParameterNode
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification, ParameterDict


class ParameterNodeV1(BaseParameterNode[Vector1]):
    _type = Vector1

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[Vector1] = None,
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
            ParameterSpecification.OFFSET,
            ParameterSpecification.SCALE
        ]
        super().set_specification(specification)

    def to_float(self) -> float:
        return self.get_value()[0]

    def reset(self) -> None:
        filler: float = 0.
        if self.get_specification() == ParameterSpecification.SCALE:
            filler = 1.
        self.set_value(Vector1(filler))

    def to_vector3(self) -> Vector3:
        filler: float = 0.
        if self.get_specification() == ParameterSpecification.SCALE:
            filler = 1.
        list_: tp.List[float] = [filler for _ in range(3)]
        list_[self.index()] = self.to_float()
        return Vector3(list_)

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        self.set_specification(ParameterDict.from_string(words[0]))
        self._index = int(words[1])
        return self._data.read_rest(words[2:])

    def write(self) -> tp.List[str]:
        words: tp.List[str] = [ParameterDict.from_specification(self._specification), str(self._index)] + self._data.write()
        return words