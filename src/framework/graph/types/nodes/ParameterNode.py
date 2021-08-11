import enum
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.Graph import Node
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector1, Vector2, Vector3
from utils.TwoWayDict import TwoWayDict

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.protocols.Measurement2D import SubMeasurement2D

SubParameterNode = tp.TypeVar('SubParameterNode', bound='ParameterNode')

T = tp.TypeVar('T')


class ParameterSpecification(enum.Enum):
    BIAS = 'bias'
    OFFSET = 'offset'
    SCALE = 'scale'
    UNIFORM_TRANSLATION_SCALE = 'uniform_translation_scale'


class ParameterDict(object):
    _parameters: TwoWayDict = TwoWayDict()
    for specification in ParameterSpecification:
        _parameters[specification] = specification.value

    @classmethod
    def from_string(cls, string: str) -> ParameterSpecification:
        assert string in cls._parameters
        return cls._parameters[string]

    @classmethod
    def from_specification(cls, specification: ParameterSpecification) -> str:
        assert specification in cls._parameters
        return cls._parameters[specification]


class ParameterNode(tp.Generic[T], Node[T]):
    _specification: ParameterSpecification

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            timestamp: tp.Optional[float] = None,
            specification: ParameterSpecification = ParameterSpecification.BIAS
    ):
        if name is None:
            name = f'{self.__class__.__name__}({ParameterDict.from_specification(specification)})'
        super().__init__(name=name, id_=id_, value=value, timestamp=timestamp)

        self.set_specification(specification)

    def get_specification(self) -> ParameterSpecification:
        return self._specification

    def set_specification(self, specification: ParameterSpecification) -> None:
        self._specification = specification

    @abstractmethod
    def to_list3(self, filler: tp.Optional[float] = None) -> tp.List[tp.Optional[float]]:
        pass

    @abstractmethod
    def to_vector3(self, filler: float = 0.) -> Vector3:
        pass

    @abstractmethod
    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        pass

    # Printable
    def to_id(self) -> str:
        return f'{self.get_id()}; {ParameterDict.from_specification(self._specification)}'

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        self._specification = ParameterDict.from_string(words[0])
        return self._data.read_rest(words[1:])

    def write(self) -> tp.List[str]:
        words: tp.List[str] = [ParameterDict.from_specification(self._specification)] + self._data.write()
        return words


def compose_bias(
        measurement: 'SubMeasurement2D',
        parameter: SE2,
        is_inverse: bool
) -> 'SubMeasurement2D':
    if is_inverse:
        parameter = parameter.inverse()

    transformation: SE2 = measurement.transformation()
    measurement.mask(transformation * parameter)
    return measurement

def compose_offset(
        measurement: 'SubMeasurement2D',
        parameter: SE2,
        is_inverse: bool
) -> 'SubMeasurement2D':
    if is_inverse:
        parameter = parameter.inverse()

    transformation: SE2 = measurement.transformation()
    measurement.mask(parameter * transformation * parameter.inverse())
    return measurement

def compose_scale(
        measurement: 'SubMeasurement2D',
        parameter: Vector3,
        is_inverse: bool
) -> 'SubMeasurement2D':
    if is_inverse:
        parameter = Vector3(np.reciprocal(parameter.array()))

    transformation: SE2 = measurement.transformation()
    measurement.mask(
        SE2.from_translation_angle_vector(
            Vector3(np.multiply(parameter.array(), transformation.translation_angle_vector().array()))
        )
    )
    return measurement


class ParameterNodeSE2(ParameterNode[SE2]):
    _type = SE2

    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in (
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET
        )
        return super().set_specification(specification)

    def to_list3(self) -> tp.List[float]:
        return self.to_vector3().to_list()

    def to_vector3(self) -> Vector3:
        return self.get_value().translation_angle_vector()

    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        if self.get_specification() == ParameterSpecification.BIAS:
            return self.compose_as_bias(measurement, is_inverse)
        else:
            return self.compose_as_offset(measurement, is_inverse)

    def compose_as_bias(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        return compose_bias(measurement, self.get_value(), is_inverse)

    def compose_as_offset(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        return compose_offset(measurement, self.get_value(), is_inverse)


class ParameterNodeV1(ParameterNode[Vector1]):
    _type = Vector1
    _index: int

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[Vector1] = None,
            index: tp.Optional[int] = 0,
            timestamp: tp.Optional[float] = None,
            specification: ParameterSpecification = ParameterSpecification.BIAS
    ):
        super().__init__(name=name, id_=id_, value=value, timestamp=timestamp, specification=specification)
        self.set_index(index)

    def set_index(self, index: int):
        assert index < 3
        self._index = index

    def get_float(self) -> float:
        return self.get_value()[0]

    # specification
    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in (
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET,
            ParameterSpecification.SCALE,
            ParameterSpecification.UNIFORM_TRANSLATION_SCALE
        )
        return super().set_specification(specification)

    def to_list3(self, filler: tp.Optional[float] = None) -> tp.List[tp.Optional[float]]:
        list_: tp.List[tp.Optional[float]] = [filler for _ in range(3)]
        list_[self._index] = self.get_float()
        return list_

    def to_vector3(self, filler: float = 0.) -> Vector3:
        return Vector3(self.to_list3(filler))

    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        if self.get_specification() == ParameterSpecification.BIAS:
            return self.compose_as_bias(measurement, is_inverse)
        if self.get_specification() == ParameterSpecification.OFFSET:
            return self.compose_as_offset(measurement, is_inverse)
        if self.get_specification() == ParameterSpecification.SCALE:
            return self.compose_as_scale(measurement, is_inverse)
        return self.compose_as_uniform_translation_scale(measurement, is_inverse)

    def compose_as_bias(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        bias = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_bias(measurement, bias, is_inverse)

    def compose_as_offset(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        offset = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_offset(measurement, offset, is_inverse)

    def compose_as_scale(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        scale = self.to_vector3(filler=1.)
        return compose_scale(measurement, scale, is_inverse)

    def compose_as_uniform_translation_scale(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        assert measurement.has_translation()
        translation: Vector2 = measurement.translation()
        scale: float = self.get_float()
        if is_inverse:
            scale = 1 / scale

        measurement.set_translation(
            Vector2(scale * translation.array())
        )
        return measurement

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = super().read(words)
        self._index = int(words[0])
        return words[1:]

    def write(self) -> tp.List[str]:
        words: tp.List[str] = super().write() + [str(self._index)]
        return words


class ParameterNodeV2(ParameterNode[Vector2]):
    _type = Vector2
    _index: int

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[Vector1] = None,
            index: tp.Optional[int] = 0,
            timestamp: tp.Optional[float] = None,
            specification: ParameterSpecification = ParameterSpecification.BIAS
    ):
        super().__init__(name=name, id_=id_, value=value, timestamp=timestamp, specification=specification)
        self.set_index(index)

    def set_index(self, index: int):
        assert index < 3
        self._index = index

    # specification
    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in (
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET,
            ParameterSpecification.SCALE
        )
        return super().set_specification(specification)

    def to_list3(self, filler: tp.Optional[float] = None) -> tp.List[tp.Optional[float]]:
        list_: tp.List[tp.Optional[float]] = self.get_value().to_list()
        list_.insert(self._index, filler)
        return list_

    def to_vector3(self, filler: float = 0.) -> Vector3:
        return Vector3(self.to_list3(filler))

    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        if self.get_specification() == ParameterSpecification.BIAS:
            return self.compose_as_bias(measurement, is_inverse)
        if self.get_specification() == ParameterSpecification.OFFSET:
            return self.compose_as_offset(measurement, is_inverse)
        return self.compose_as_scale(measurement, is_inverse)

    def compose_as_bias(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        bias = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_bias(measurement, bias, is_inverse)

    def compose_as_offset(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        offset = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_offset(measurement, offset, is_inverse)

    def compose_as_scale(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        scale = self.to_vector3(filler=1.)
        return compose_scale(measurement, scale, is_inverse)


class ParameterNodeV3(ParameterNode[Vector3]):
    _type = Vector3

    # specification
    def set_specification(self, specification: ParameterSpecification) -> None:
        assert specification in (
            ParameterSpecification.SCALE
        )
        return super().set_specification(specification)

    def to_list3(self) -> tp.List[float]:
        return self.to_vector3().to_list()

    def to_vector3(self) -> Vector3:
        return self.get_value()

    def compose(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        return self.compose_as_scale(measurement, is_inverse)

    def compose_as_scale(
            self,
            measurement: 'SubMeasurement2D',
            is_inverse: bool = False
    ) -> 'SubMeasurement2D':
        scale = self.to_vector3()
        return compose_scale(measurement, scale, is_inverse)


class ParameterNodeFactory(object):
    _map: tp.Dict['Quantity', tp.Type[SubParameterNode]] = {
        SE2: ParameterNodeSE2,
        Vector1: ParameterNodeV1,
        Vector2: ParameterNodeV2,
        Vector3: ParameterNodeV3
    }

    @classmethod
    def from_value_type(
            cls,
            value_type: tp.Type['Quantity']
    ) -> tp.Type[SubParameterNode]:
        assert value_type in cls._map, f"ParameterNode with value type '{value_type}' not known."
        return cls._map[value_type]

    @classmethod
    def from_value(
            cls,
            value: 'Quantity',
            specification: ParameterSpecification = ParameterSpecification.BIAS,
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
            specification=specification
        )
        return node
