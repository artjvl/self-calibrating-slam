from abc import ABC, abstractmethod

from src.structures import *
from src.groups.Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, matrix):
        assert isinstance(matrix, Square)
        self._matrix = matrix

    # abstract implementations
    def matrix(self):
        return self._matrix

    @classmethod
    def from_matrix(cls, matrix):
        assert isinstance(matrix, Square)
        return cls(matrix)

    # abstract methods
    @abstractmethod
    def jacobian(self):
        """ returns the left Jacobian of the group element """
        pass

    @abstractmethod
    def inverse_jacobian(self):
        """ returns the inverse left Jacobian of the group element """
        pass
