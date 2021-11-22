import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.data.DataFactory import DataFactory
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.vector import VectorFactory, Vector2, Vector3
from src.framework.simulation.Parameter import StaticParameter

if tp.TYPE_CHECKING:
    from src.framework.graph.data import SubData
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubParameterNode
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.simulation.Parameter import SubParameter

T = tp.TypeVar('T')
SubSensor = tp.TypeVar('SubSensor', bound='Sensor')


class Sensor(tp.Generic[T]):
    _type: tp.Type[T]
    _rng: np.random.RandomState

    _info_matrix: 'SubSquare'
    _parameters: tp.Dict[str, 'SubParameter']

    def __init__(
            self,
            seed: tp.Optional[int] = None,
            info_matrix: tp.Optional['SubSquare'] = None
    ):
        self.set_rng(seed)

        # information
        if info_matrix is None:
            info_matrix = SquareFactory.from_dim(self.dim()).identity()
        self._info_matrix = info_matrix
        self._parameters = {}

    # measurement-type
    @classmethod
    def dim(cls):
        return DataFactory.from_type(cls.type()).dim()

    @classmethod
    def type(cls) -> tp.Type['SubData']:
        return cls._type

    # info
    def set_info_matrix(self, info_matrix: 'SubSquare') -> None:
        self._info_matrix = info_matrix

    def get_info_matrix(self) -> 'SubSquare':
        return self._info_matrix

    def set_cov_matrix(self, cov_matrix: 'SubSquare') -> None:
        self._info_matrix = cov_matrix.inverse()

    def get_cov_matrix(self) -> 'SubSquare':
        return self._info_matrix.inverse()

    # noise
    def set_rng(self, seed: tp.Optional[int] = None) -> None:
        self._rng = np.random.RandomState(seed)

    def generate_noise(self) -> 'SubSizeVector':
        dim: int = self.dim()
        vector_type: tp.Type['SubSizeVector'] = VectorFactory.from_dim(dim)
        return vector_type(
            self._rng.multivariate_normal(
                mean=[0] * dim,
                cov=self.get_info_matrix().inverse().array()
            )
        )

    # parameters
    def has_parameter(self, name: str) -> bool:
        return name in self._parameters

    def add_parameter(
            self,
            name: str,
            parameter: 'SubParameter'
    ) -> 'SubParameterNode':
        assert name not in self._parameters, f'{name}'
        parameter.set_name(name)
        self._parameters[name] = parameter
        return parameter.node()

    def update_parameter(
            self,
            name: str,
            value: 'Quantity'
    ) -> 'SubParameterNode':
        assert name in self._parameters, f'{name}'
        parameter: 'SubParameter' = self._parameters[name]
        assert isinstance(parameter, StaticParameter)
        return parameter.update(value)

    def get_parameter(
            self,
            name: str
    ) -> 'SubParameter':
        assert self.has_parameter(name)
        return self._parameters[name]

    def get_parameters(
            self,
            is_reverse: bool = False
    ) -> tp.List['SubParameter']:
        if is_reverse:
            return list(reversed(self._parameters.values()))
        return list(self._parameters.values())

    @abstractmethod
    def measure(self, value: T) -> T:
        """ Adds noise to the value. """
        pass

    @abstractmethod
    def compose(self, value: T) -> T:
        """ Composes the value by sequentially adding all stored parameters. """
        pass

    @abstractmethod
    def decompose(self, value: T) -> T:
        """ Decomposes the value by, in reverse order, subtracting all stored parameters. """
        pass

    @classmethod
    def from_info_matrix(
            cls,
            seed: tp.Optional[int] = None,
            info_matrix: tp.Optional['SubSquare'] = None
    ) -> SubSensor:
        return cls(seed, info_matrix)

    @classmethod
    def from_cov_matrix(
            cls,
            seed: tp.Optional[int] = None,
            cov_matrix: tp.Optional['SubSquare'] = None
    ) -> SubSensor:
        info_matrix: tp.Optional['SubSquare'] = None
        if cov_matrix is not None:
            info_matrix = cov_matrix.inverse()
        return cls(seed, info_matrix)


class SensorSE2(Sensor[SE2]):
    _type = SE2

    def measure(self, value: SE2) -> SE2:
        noise: Vector3 = self.generate_noise()
        return value.oplus(noise)

    def compose(self, value: SE2) -> SE2:
        transformation: SE2 = value
        for parameter in self.get_parameters():
            transformation = parameter.compose(transformation)
        return transformation

    def decompose(self, value: SE2) -> SE2:
        transformation: SE2 = value
        for parameter in self.get_parameters(is_reverse=True):
            transformation = parameter.compose(transformation, is_inverse=True)
        return transformation


class SensorV2(Sensor[Vector2]):
    _type = Vector2

    def measure(self, value: Vector2) -> Vector2:
        noise: Vector2 = self.generate_noise()
        return Vector2(value.array() + noise.array())

    def compose(self, value: Vector2) -> Vector2:
        transformation: SE2 = SE2.from_translation_angle(value, 0.)
        for parameter in self.get_parameters():
            transformation = parameter.compose_translation(transformation)
        return transformation.translation()

    def decompose(self, value: Vector2) -> Vector2:
        for parameter in self.get_parameters()[::-1]:
            value = parameter.compose_translation(value, inverse=True)
        return value


class SensorFactory(object):
    _map: tp.Dict[tp.Type['Quantity'], tp.Type[SubSensor]] = {
        SE2: SensorSE2,
        Vector2: SensorV2
    }

    @classmethod
    def from_type(
            cls,
            type_: tp.Type['Quantity']
    ) -> tp.Type[SubSensor]:
        assert type_ in cls._map, f'{type_}'
        return cls._map[type_]

    @classmethod
    def from_value(
            cls,
            type_: tp.Type['Quantity'],
            info_matrix: tp.Optional['SubSquare'] = None,
            seed: tp.Optional[int] = None
    ):
        return cls.from_type(type_)(seed, info_matrix)
