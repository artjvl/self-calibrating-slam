import typing as tp

from src.framework.math.matrix.vector import Vector2, Vector3
from src.framework.ppg.parameter.BaseParameterNode import BaseParameterNode
from src.framework.ppg.parameter.ParameterSpecification import ParameterSpecification, ParameterDict


class ParameterNodeV2(BaseParameterNode[Vector2]):
    _type = Vector2

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[Vector2] = None,
            specification: ParameterSpecification = ParameterSpecification.BIAS,
            timestep: int = 0,
            index: int = 0
    ):
        super().__init__(name, id_, value, specification, timestep, index)

    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in [
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET,
            ParameterSpecification.SCALE
        ]
        super().set_specification(specification)

    def reset(self) -> None:
        filler: float = 0.
        if self.get_specification() == ParameterSpecification.SCALE:
            filler = 1.
        list_: tp.List[float] = [filler for _ in range(2)]
        self.set_value(Vector2(list_))

    def to_vector3(self) -> Vector3:
        filler: float = 0.
        if self.get_specification() == ParameterSpecification.SCALE:
            filler = 1.
        list_: tp.List[float] = self.get_value().to_list()
        list_.insert(self.index(), filler)
        return Vector3(list_)

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        self.set_specification(ParameterDict.from_string(words[0]))
        self._index = int(words[1])
        return self._data.read_rest(words[2:])

    def write(self) -> tp.List[str]:
        words: tp.List[str] = [ParameterDict.from_specification(self._specification), str(self._index)] + self._data.write()
        return words