import numpy as np
from abc import ABC, abstractmethod

from src.framework.structures import *
from src.framework.groups.Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, matrix: Square):
        self._matrix = matrix

    # public methods
    def inverse(self):
        return type(self).from_matrix(Square(np.transpose(self.matrix())))

    @abstractmethod
    def angle(self) -> float:
        pass

    @abstractmethod
    def jacobian(self) -> Square:
        """ returns the left Jacobian of the group element """
        pass

    @abstractmethod
    def inverse_jacobian(self) -> Square:
        """ returns the inverse left Jacobian of the group element """
        pass

    # alternative representations
    def matrix(self) -> Square:
        return self._matrix

    # alternative constructors
    @classmethod
    def from_matrix(cls, matrix: Square):
        return cls(matrix)
