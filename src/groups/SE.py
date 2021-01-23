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

    # public class-methods
    @classmethod
    def from_vectors(cls, translation_vector, rotation_vector):
        assert isinstance(translation_vector, Vector)
        assert isinstance(rotation_vector, Vector)
        vector = np.vstack((translation_vector, rotation_vector))
        return cls.from_vector(vector)

    @classmethod
    def elements(cls):
        elements = list()
        translation_elements = Vector.axes(cls._dim)
        for element in translation_elements:
            padded = np.pad(element, [(0, 1), (cls._dim, 0)])
            elements.append(padded)
        rotation_elements = cls._rotation_type.elements()
        for element in rotation_elements:
            padded = np.pad(element, [(0, 1), (0, 1)])
            elements.append(padded)
        return elements

    # private class-methods
    @classmethod
    def _construct_matrix(cls, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO)
        padded_translation = np.pad(np.vstack((translation, 1)), [(0, 0), (cls._dim, 0)])
        padded_rotation = np.pad(rotation, [(0, 1), (0, 1)])
        return Square(padded_translation + padded_rotation)

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
    def _rotation_type(cls):
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

    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = 0
        for i, element in enumerate(elements):
            algebra += vector[i] * element
        return algebra
