from abc import ABC, abstractmethod

from src.structures import *
from src.groups.Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, matrix):
        assert isinstance(matrix, Square)
        self._matrix = matrix

    # abstract methods
    @abstractmethod
    def left_jacobian(self):
        """ returns the left Jacobian of the group element """
        pass

    @staticmethod
    @abstractmethod
    def elements():
        """ returns the list of base elements """
        pass

    # abstract implementations
    def matrix(self):
        return self._matrix

    @classmethod
    def from_matrix(cls, matrix):
        return cls(matrix)

    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = 0
        for i, element in elements:
            algebra += vector[i] * element
        return algebra
