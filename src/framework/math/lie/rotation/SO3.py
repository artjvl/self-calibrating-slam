from __future__ import annotations
import typing as tp

import numpy as np
from src.framework.math.lie.rotation.SO import SO
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector3
if tp.TYPE_CHECKING:
    from src.framework.math.lie.rotation.SO2 import SO2


class SO3(SO):
    _dim = 3
    _dof = 3

    def __init__(self, matrix: Square3):
        super().__init__(matrix)

    # conversion
    def to_so2(self) -> 'SO2':
        from src.framework.math.lie.rotation.SO2 import SO2
        return SO2.from_angle(self.vector()[2])

    # properties
    def angle(self) -> float:
        return self.vector().magnitude()

    def inverse(self) -> SO3:
        return super().inverse()

    def jacobian(self) -> Square3:
        vector: Vector3 = self.vector()
        algebra_array: np.ndarray = self._vector_to_algebra(vector).array()
        angle: float = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix_array: np.ndarray = np.eye(3) + 0.5 * algebra_array
        else:
            unit_algebra_array: np.ndarray = algebra_array / angle
            matrix_array = np.eye(3) + ((1 - np.cos(angle)) / angle) * unit_algebra_array + \
                (1 - np.sin(angle) / angle) * (unit_algebra_array @ unit_algebra_array)
        return Square3(matrix_array)

    def inverse_jacobian(self) -> Square3:
        vector: Vector3 = self.vector()
        algebra_array: np.ndarray = self._vector_to_algebra(vector).array()
        angle: float = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix_array = np.eye(3) + 0.5 * algebra_array
        else:
            unit_algebra_array: np.ndarray = algebra_array / angle
            matrix_array = np.eye(3) - 0.5 * algebra_array + \
                (1 - 0.5 * angle * np.sin(angle) / (1 - np.cos(angle))) * (unit_algebra_array @ unit_algebra_array)
        return Square3(matrix_array)

    # alternative representations
    def algebra(self) -> Square3:
        return super().algebra()

    def vector(self) -> Vector3:
        matrix: np.ndarray = self.matrix().array()
        angle: float = np.arccos(0.5 * (np.trace(matrix) - 1))
        algebra: np.ndarray
        if np.isclose(angle, 0.):
            algebra = matrix - np.eye(3)
        else:
            algebra = (angle * (matrix - np.transpose(matrix))) / (2 * np.sin(angle))
        return type(self)._algebra_to_vector(Square3(algebra))

    def matrix(self) -> Square3:
        return super().matrix()

    # alternative creators
    @classmethod
    def from_vector(cls, vector: Vector3) -> SO3:
        algebra_array: np.ndarray = cls._vector_to_algebra(vector).array()
        angle: float = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix_array = np.eye(3) + algebra_array
        else:
            unit_algebra_array = algebra_array / angle
            matrix_array = np.eye(3) + np.sin(angle) * unit_algebra_array + \
                (1 - np.cos(angle)) * (unit_algebra_array @ unit_algebra_array)
        return cls(Square3(matrix_array))

    @classmethod
    def from_elements(cls, *args: float) -> SO3:
        return super().from_elements(*args)

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: Vector3) -> Square3:
        a: float = vector[0]
        b: float = vector[1]
        c: float = vector[2]
        return Square3([[0, -c, b],
                        [c, 0, -a],
                        [-b, a, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: Square3) -> Vector3:
        return Vector3([algebra[2, 1],
                        algebra[0, 2],
                        algebra[1, 0]])
