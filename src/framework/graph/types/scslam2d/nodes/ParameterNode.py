import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.Graph import Node
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3

SubParameterNode = tp.TypeVar('SubParameterNode', bound='ParameterNode')
T = tp.TypeVar('T')


class ParameterNode(tp.Generic[T], Node[T]):

    _next: tp.Optional[SubParameterNode]

    def __init__(
            self,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            timestamp: tp.Optional[float] = None,
            next_: tp.Optional[SubParameterNode] = None
    ):
        super().__init__(id_, value, timestamp)
        self._next = next_

    def get_next(self) -> SubParameterNode:
        assert self.has_next()
        return self._next

    def has_next(self) -> bool:
        return self._next is not None

    def set_next(self, next_: SubParameterNode):
        assert not self.has_next()
        assert type(next_) == type(self)
        self._next = next_

    # composition
    @abstractmethod
    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        """
        Composition of a value:
        - inverse = True: add parameter to value
              e.g. convert measurement (= transformation - parameter) to transformation
        - inverse = False: subtract parameter to value
              e.g. convert transformation (= measurement + parameter) to measurement
        """
        pass

    def compose_translation(
            self,
            translation: Vector2,
            inverse: bool = False
    ) -> Vector2:
        transformation: SE2 = SE2.from_translation_angle(translation, 0)
        composed: SE2 = self.compose_transformation(transformation, inverse=inverse)
        return composed.translation()


class BiasParameterNode(ParameterNode[SE2]):

    _type = SE2

    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        parameter: SE2 = self.get_value()
        if inverse:
            parameter = parameter.inverse()
        return transformation * parameter


class OffsetParameterNode(ParameterNode[SE2]):

    _type = SE2

    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        parameter: SE2 = self.get_value()
        if inverse:
            parameter = parameter.inverse()
        return parameter * transformation * parameter.inverse()


class ScaleParameterNode(ParameterNode[Vector3]):

    _type = Vector3

    def compose_transformation(
            self,
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        parameter: Vector3 = self.get_value()
        if inverse:
            parameter = Vector3(1 / parameter.array())
        return SE2.from_translation_angle_vector(
            Vector3(np.multiply(parameter.array(), transformation.translation_angle_vector().array()))
        )