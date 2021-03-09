from __future__ import annotations

from typing import *
from abc import ABC, abstractmethod

from src.framework.structures import *


class Group(ABC):

    # static attributes
    @property
    @classmethod
    @abstractmethod
    def _dim(cls) -> int:
        """ number of dimensions """
        pass

    @property
    @classmethod
    @abstractmethod
    def _dof(cls) -> int:
        """ number of degrees of freedom """
        pass

    # operators
    def __mul__(self, other: Union[Group, Vector]):
        if isinstance(other, Group):
            return self.from_matrix(self.matrix() @ other.matrix())
        if isinstance(other, Vector):
            return Vector(self.matrix() @ other)

    def __neg__(self):
        matrix = self.matrix()
        return type(self).from_matrix(- matrix)

    def __add__(self, other: Group) -> Group:
        return self * other

    def __sub__(self, other: Group) -> Group:
        return other.inverse() * self

    # public methods
    def algebra(self):
        vector = self.vector()
        algebra = type(self)._vector_to_algebra(vector)
        return algebra

    # alternative representations
    @abstractmethod
    def matrix(self) -> Square:
        """ returns the matrix representation """
        pass

    def vector(self) -> Vector:
        """ returns the vector representation """
        pass

    def inverse(self) -> Group:
        """ returns the inverted group element """
        pass

    # alternative constructors
    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix: Square):
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_vector(cls, vector: Vector):
        """ generates group element from vector """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args, **kwargs):
        """ generates group element from vector elements """
        pass

    # helper-methods
    @staticmethod
    @abstractmethod
    def _vector_to_algebra(vector: Vector) -> Square:
        """ returns the algebra corresponding to the vector """
        pass

    @staticmethod
    @abstractmethod
    def _algebra_to_vector(algebra: Square) -> Vector:
        """ returns the vector corresponding to the algebra """
        pass

    # object methods
    def __str__(self):
        matrix = self.matrix()
        return str(matrix)
