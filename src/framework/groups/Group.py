from __future__ import annotations

import typing as tp
from abc import ABC, abstractmethod

from src.framework.structures.Square import Square
from src.framework.structures.Vector import Vector, SubVector

SubGroup = tp.TypeVar('SubGroup', bound='Group')


class Group(ABC):

    _dim: int
    _dof: int

    # operators
    def __mul__(self, other: tp.Union[Group, Vector]) -> tp.Union[SubGroup, SubVector]:
        if isinstance(other, Group):
            return self.from_matrix(self.matrix() @ other.matrix())
        if isinstance(other, Vector):
            return Vector(self.matrix() @ other)

    def __neg__(self) -> SubGroup:
        matrix = self.matrix()
        return type(self).from_matrix(- matrix)

    def __add__(self, other: Group) -> SubGroup:
        return self * other

    def __sub__(self, other: Group) -> SubGroup:
        return other.inverse() * self

    # public methods
    def algebra(self) -> Square:
        vector = self.vector()
        algebra = type(self)._vector_to_algebra(vector)
        return algebra

    # alternative representations
    @abstractmethod
    def matrix(self) -> Square:
        """ returns the matrix representation """
        pass

    def vector(self) -> SubVector:
        """ returns the vector representation """
        pass

    def inverse(self) -> SubGroup:
        """ returns the inverted group element """
        pass

    # alternative constructors
    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix: Square) -> SubGroup:
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_vector(cls, vector: Vector) -> SubGroup:
        """ generates group element from vector """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args, **kwargs) -> SubGroup:
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
    def __str__(self) -> str:
        matrix = self.matrix()
        return str(matrix)
