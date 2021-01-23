import numpy as np
from abc import ABC, abstractmethod

from src.structures import *
from src.groups.Group import Group
from src.groups.SO import SO


class SE(Group, ABC):

    # constructor
    def __init__(self, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO)
        self._translation = translation
        self._rotation = rotation

    # public methods
    def translation(self):
        return self._translation

    def rotation(self):
        return self._rotation

    def vector(self):
        rotation = self.rotation()
        translation = self.translation()
        rotation_vector = rotation.vector()
        inverse_jacobian = rotation.inverse_jacobian()
        translation_vector = inverse_jacobian * translation
        vector = np.vstack((translation_vector, rotation_vector))
        return Vector(vector)

    # public class-methods
    @classmethod
    def from_vectors(cls, translation_vector, rotation_vector):
        assert isinstance(translation_vector, Vector)
        assert isinstance(rotation_vector, Vector)
        rotation = cls._rotation_type.from_vector(rotation_vector)
        jacobian = rotation.jacobian()
        translation = jacobian * translation_vector
        return cls(translation, rotation)

    @classmethod
    def from_vector(cls, vector):
        assert isinstance(vector, Vector)
        translation_vector = vector[0: cls._dim]
        rotation_vector = vector[cls._dim + 1:]
        return cls.from_vectors(translation_vector, rotation_vector)

    # @classmethod
    # def elements(cls):
    #     elements = list()
    #     translation_elements = Vector.axes(cls._dim)
    #     for element in translation_elements:
    #         padded = cls._pad_translation(element)
    #         elements.append(padded)
    #     rotation_elements = cls._rotation_type.elements()
    #     for element in rotation_elements:
    #         padded = cls._pad_rotation(element)
    #         elements.append(padded)
    #     return elements

    # private class-methods
    @classmethod
    def _pad_translation(cls, translation, extra=0):
        assert isinstance(translation, Vector)
        return Square(np.pad(np.vstack((translation, extra)), [(0, 0), (cls._dim, 0)]))

    @classmethod
    def _pad_rotation(cls, rotation):
        assert isinstance(rotation, Square)
        return Square(np.pad(rotation, [(0, 1), (0, 1)]))

    @classmethod
    def _construct_matrix(cls, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO)
        padded_translation = cls._pad_translation(translation, extra=1)
        padded_rotation = cls._pad_rotation(rotation)
        return padded_translation + padded_rotation

    @classmethod
    def _extract_translation(cls, matrix):
        assert isinstance(matrix, Square)
        return matrix[-1][0: cls._dim]

    @classmethod
    def _extract_rotation(cls, matrix):
        assert isinstance(matrix, Square)
        return matrix[0: cls._dim][0: cls._dim]

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def _rotation_type(cls) -> SO:
        pass

    # abstract implementations
    def matrix(self):
        return self._construct_matrix(self._translation, self._rotation)

    @classmethod
    def from_matrix(cls, matrix):
        assert isinstance(matrix, Square)
        translation = cls._extract_translation(matrix)
        rotation = cls._extract_rotation(matrix)
        return cls(translation, rotation)
