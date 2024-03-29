from __future__ import annotations

import numpy as np

from src.framework.math.lie.rotation.SO3 import SO3
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.matrix.square import Square2
from src.framework.math.matrix.vector import Vector1, Vector3


class SO2(SO):
    _dim = 2
    _dof = 1
    _angle: float

    def __init__(self, matrix: Square2):
        super().__init__(matrix)
        self._angle = np.arctan2(matrix[1, 0], matrix[0, 0])

    def __mul__(self, other: SO2):
        assert type(self) == type(other)
        return self.from_angle(self.angle() + other.angle())

    # conversion
    def to_so3(self) -> SO3:
        vector = Vector3(0, 0, self.angle())
        return SO3.from_vector(vector)

    # properties
    def angle(self) -> float:
        return self._angle

    def inverse(self) -> SO2:
        return type(self).from_angle(- self._angle)

    def jacobian(self) -> Square2:
        angle: float = self.angle()
        if np.isclose(angle, 0.):
            return Square2(np.eye(2) + 0.5 * self.algebra().array())
        sin_angle: float = np.sin(angle)
        cos_angle: float = np.cos(angle)
        matrix_array: np.ndarray = (1 / angle) * np.array([[sin_angle, cos_angle - 1.],
                                                           [1. - cos_angle, sin_angle]])
        return Square2(matrix_array)

    def inverse_jacobian(self) -> Square2:
        jacobian: Square2 = self.jacobian()
        a: float = jacobian[0, 0]
        b: float = jacobian[1, 0]
        matrix_array: np.ndarray = (1 / (a**2 + b**2)) * np.array([[a, b],
                                                                   [-b, a]])
        return Square2(matrix_array)

    # alternative representations
    def algebra(self) -> Square2:
        return super().algebra()

    def vector(self) -> Vector1:
        return Vector1(self._angle)

    def matrix(self) -> Square2:
        return self._angle_to_matrix(self._angle)

    # alternative creators
    @classmethod
    def from_angle(cls, angle: float) -> SO2:
        return cls(
            cls._angle_to_matrix(angle)
        )

    @classmethod
    def from_vector(cls, vector: Vector1) -> SO2:
        return cls.from_angle(vector[0])

    @classmethod
    def from_elements(cls, *args: float) -> SO2:
        return super().from_elements(*args)

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: Vector1) -> Square2:
        a: float = vector[0]
        return Square2([[0, -a],
                        [a, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: Square2) -> Vector1:
        return Vector1(algebra[1, 0])

    @staticmethod
    def _angle_to_matrix(angle: float) -> Square2:
        sin_angle: float = np.sin(angle)
        cos_angle: float = np.cos(angle)
        array = np.array([[cos_angle, -sin_angle],
                          [sin_angle, cos_angle]])
        return Square2(array)
