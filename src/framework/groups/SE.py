from __future__ import annotations

from abc import ABC, abstractmethod
from typing import *

import numpy as np

from src.framework.groups.Group import Group
from src.framework.groups.SO import SO
from src.framework.structures import *

R = TypeVar('R', bound=SO)


class SE(Generic[R], Group, ABC):

    # constructor
    def __init__(self, translation: Vector, rotation: R):
        self._translation = translation
        self._rotation = rotation

    # static properties
    @property
    @classmethod
    @abstractmethod
    def _rotation_type(cls) -> R:
        pass

    # public methods
    def translation(self) -> Vector:
        return self._translation

    def rotation(self) -> R:
        return self._rotation

    def plus(self, vector: Vector):
        increment: SE = type(self).from_vector(vector)
        return self + increment
        # return self * increment

    def minus(self, transformation: SE) -> Vector:
        # difference: SE = transformation.inverse() * self
        difference: SE = self - transformation
        return difference.vector()

    def inverse(self):
        translation = self.translation()
        rotation = self.rotation()
        inverse_rotation = rotation.inverse()
        inverse_translation = - inverse_rotation * translation
        return type(self)(inverse_translation, inverse_rotation)

    # alternative representations
    def matrix(self) -> Square:
        return self._construct_matrix(self._translation, self._rotation)

    def vector(self) -> Vector:
        rotation = self.rotation()
        translation = self.translation()
        rotation_vector = rotation.vector()
        inverse_jacobian = rotation.inverse_jacobian()
        translation_vector = Vector(inverse_jacobian @ translation)
        vector = Vector(np.vstack((translation_vector, rotation_vector)))
        return vector

    # alternative constructors
    @classmethod
    def from_matrix(cls, matrix: Square):
        translation = cls._extract_translation(matrix)
        rotation = cls._extract_rotation(matrix)
        return cls(translation, rotation)

    @classmethod
    def from_vector(cls, vector: Vector):
        translation_vector = vector[0: cls._dim]
        rotation_vector = vector[cls._dim:]
        return cls.from_vectors(translation_vector, rotation_vector)

    @classmethod
    def from_vectors(cls, translation_vector: Vector, rotation_vector: Vector):
        rotation = cls._rotation_type.from_vector(rotation_vector)
        jacobian = rotation.jacobian()
        translation = Vector(jacobian @ translation_vector)
        return cls(translation, rotation)

    # helper-methods
    @classmethod
    def _construct_matrix(cls, translation: Vector, rotation: R) -> Square:
        rotation_matrix = rotation.matrix()
        pad = np.zeros((1, cls._dim))
        matrix = np.block([[rotation_matrix, translation],
                           [pad, 1]])
        return Square(matrix)

    @classmethod
    def _extract_translation(cls, matrix: Square) -> Vector:
        translation = Vector(matrix[: cls._dim, cls._dim:])
        return translation

    @classmethod
    def _extract_rotation(cls, matrix: Square) -> R:
        matrix = Square(matrix[: cls._dim, : cls._dim])
        rotation = cls._rotation_type.from_matrix(matrix)
        return rotation
