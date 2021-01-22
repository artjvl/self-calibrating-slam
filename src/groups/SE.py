import numpy as np
from abc import ABC, abstractmethod

from src.structures import *
from src.groups.Group import Group
from src.groups.SO import SO


class SE(Group, ABC):

    # constructor
    def __init__(self, vector, matrix=None, translation=None, rotation=None):
        assert isinstance(vector, Vector)
        vector = Vector(np.vstack((translation, rotation.vector())))
        super().__init__(vector, matrix)
        self._translation = translation
        self._rotation = rotation

    # public methods
    def translation(self):
        return self._translation

    def rotation(self):
        return self._rotation

    # public class-methods
    def from_elements(self, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO)



    @classmethod
    def elements(cls):
        elements = list()
        translation_elements = cls.translation().axes()
        for element in translation_elements:
            padded = np.pad(element, [(0, 1), (cls.n, 0)])
            elements.append(padded)
        rotation_elements = cls.rotation().elements()
        for element in rotation_elements:
            padded = np.pad(element, [(0, 1), (0, 1)])
            elements.append(padded)
        return elements

    # private class-methods
    @classmethod
    def _construct_matrix(cls, translation, rotation):
        return np.pad(np.vstack((translation, 1)), [(0, 0), (cls.n, 0)]) \
               + np.pad(rotation, [(0, 1), (0, 1)])

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        # number of dimensions
        pass

    @property
    @abstractmethod
    def m(self):
        # number of degrees of freedom
        pass

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = Square(np.zeros((cls.n + 1, cls.n + 1)))
        for index in range(cls.n + cls.m):
            algebra += vector[index] * elements[index]
        return algebra
