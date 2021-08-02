import typing as tp
from abc import abstractmethod

from src.framework.graph.Graph import Node
from src.framework.graph.data.DataFactory import Supported
from src.framework.graph.types.ParameterComposer import ParameterType, ParameterDict
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2, Vector3

SubParameterNode = tp.TypeVar('SubParameterNode', bound='ParameterNode')
ParameterData = tp.Union[SE2, Vector1, Vector2, Vector3]
T = tp.TypeVar('T')


class ParameterNode(tp.Generic[T], Node[T]):
    _interpretation: ParameterType

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            timestamp: tp.Optional[float] = None,
            interpretation: ParameterType = ParameterType.BIAS
    ):
        if name is None:
            name = f'{self.__class__.__name__}({ParameterDict.from_interpretation(interpretation)})'
        super().__init__(name=name, id_=id_, value=value, timestamp=timestamp)
        self.set_interpretation(interpretation)

    def get_interpretation(self) -> ParameterType:
        return self._interpretation

    def set_interpretation(self, interpretation: ParameterType) -> None:
        self._interpretation = interpretation

    @abstractmethod
    def to_vector3(self) -> Vector3:
        pass

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}; {ParameterDict.from_interpretation(self._interpretation)}'

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        self._interpretation = ParameterDict.from_string(words[0])
        return self._data.read_rest(words[1:])

    def write(self) -> tp.List[str]:
        words: tp.List[str] = [ParameterDict.from_interpretation(self._interpretation)] + self._data.write()
        return words


class ParameterSE2(ParameterNode[SE2]):
    _type = SE2

    def set_interpretation(self, interpretation: ParameterType) -> None:
        assert interpretation in (ParameterType.BIAS, ParameterType.OFFSET)
        return super().set_interpretation(interpretation)

    def to_vector3(self) -> Vector3:
        return self.get_value().vector()


class ParameterV1(ParameterNode[Vector1]):
    _type = Vector1
    _index: int

    def __init__(
            self,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            index: tp.Optional[int] = 0,
            timestamp: tp.Optional[float] = None,
            interpretation: ParameterType = ParameterType.BIAS,
            name: tp.Optional[str] = None
    ):
        super().__init__(id_=id_, value=value, timestamp=timestamp, interpretation=interpretation, name=name)
        self.set_index(index)

    def set_index(self, index: int):
        assert index < 3
        self._index = index

    def get_float(self) -> float:
        return self.get_value()[0]

    def set_interpretation(self, interpretation: ParameterType) -> None:
        assert interpretation in (ParameterType.BIAS, ParameterType.OFFSET, ParameterType.SCALE)
        return super().set_interpretation(interpretation)

    def to_vector3(self) -> Vector3:
        vector: Vector3 = Vector3.zeros()
        vector[self._index] = self.get_float()
        return vector

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = super().read(words)
        self._index = int(words[0])
        return words[1:]

    def write(self) -> tp.List[str]:
        words: tp.List[str] = super().write() + [str(self._index)]
        return words


class ParameterV2(ParameterNode[Vector2]):
    _type = Vector2

    def set_interpretation(self, interpretation: ParameterType) -> None:
        assert interpretation in (ParameterType.BIAS, ParameterType.OFFSET, ParameterType.SCALE)
        return super().set_interpretation(interpretation)

    def to_vector3(self) -> Vector3:
        value: Vector2 = self.get_value()
        return Vector3(value[0], value[1], 0)


class ParameterV3(ParameterNode[Vector3]):
    _type = Vector3

    def set_interpretation(self, interpretation: ParameterType) -> None:
        assert interpretation in (ParameterType.SCALE)
        return super().set_interpretation(interpretation)

    def to_vector3(self) -> Vector3:
        return self.get_value()


class ParameterNodeFactory(object):
    _map: tp.Dict[Supported, tp.Type[SubParameterNode]] = {
        SE2: ParameterSE2,
        Vector1: ParameterV1,
        Vector2: ParameterV2,
        Vector3: ParameterV3
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type[Supported]
    ) -> tp.Type[SubParameterNode]:
        assert value_type in cls._map, f"ParameterNode with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: Supported,
            interpretation: ParameterType = ParameterType.BIAS,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            timestamp: tp.Optional[float] = None
    ) -> SubParameterNode:
        node_type: tp.Type[SubParameterNode] = cls.from_value_type(type(value))
        node: SubParameterNode = node_type(
            name=name,
            id_=id_,
            value=value,
            timestamp=timestamp,
            interpretation=interpretation
        )
        return node
