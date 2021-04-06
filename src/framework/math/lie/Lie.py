import typing as tp
from abc import abstractmethod

import numpy as np

from src.framework.math.Dimensional import Dimensional
from src.framework.math.matrix.square import SubSquare, SquareFactory
from src.framework.math.matrix.vector import SubVector

SubLie = tp.TypeVar('SubLie', bound='Lie')


class Lie(Dimensional):

    _dof: int

    # operators
    def __mul__(self, other: SubLie):
        assert type(self) == type(other)
        return self.from_matrix(
            SquareFactory.from_dim(self.get_size())(self.array() @ other.array())
        )

    def __add__(self, other: SubLie) -> SubLie:
        assert type(self) == type(other)
        return self * other

    def __sub__(self, other: SubLie) -> SubLie:
        return other.inverse() * self

    # properties
    @classmethod
    def get_dof(cls) -> int:
        return cls._dof

    @classmethod
    @abstractmethod
    def get_size(cls) -> int:
        pass

    def algebra(self) -> SubSquare:
        return type(self)._vector_to_algebra(self.vector())

    # alternative representations
    @abstractmethod
    def matrix(self) -> SubSquare:
        pass

    def array(self) -> np.ndarray:
        return self.matrix().array()

    @abstractmethod
    def vector(self) -> SubVector:
        pass

    @abstractmethod
    def inverse(self) -> SubLie:
        pass

    # alternative constructors
    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix: SubSquare) -> SubLie:
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_vector(cls, vector: SubVector) -> SubLie:
        """ generates group element from vector """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args: float) -> SubLie:
        """ generates group element from vector elements """
        pass

    # helper-methods
    @staticmethod
    @abstractmethod
    def _vector_to_algebra(vector: SubVector) -> SubSquare:
        """ returns the algebra corresponding to the vector """
        pass

    @staticmethod
    @abstractmethod
    def _algebra_to_vector(algebra: SubSquare) -> SubVector:
        """ returns the vector corresponding to the algebra """
        pass

    # print
    def __str__(self):
        return np.array2string(
            self.array()
        )

    def __repr__(self):
        name: str = self.__class__.__name__
        return name + np.array2string(
            self.array(),
            prefix=name
        )
