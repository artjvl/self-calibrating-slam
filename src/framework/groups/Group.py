from abc import ABC, abstractmethod

from src.structures import *


class Group(ABC):

    # operators
    def __mul__(self, other):
        assert isinstance(other, (Group, Vector))
        if isinstance(other, Group):
            return self.from_matrix(self.matrix() @ other.matrix())
        if isinstance(other, Vector):
            return Vector(self.matrix() @ other)

    def __neg__(self):
        matrix = self.matrix()
        return type(self).from_matrix(- matrix)

    def __str__(self):
        matrix = self.matrix()
        return str(matrix)

    # public methods
    def algebra(self):
        vector = self.vector()
        algebra = type(self).vector_to_algebra(vector)
        return algebra

    # abstract properties
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

    # abstract methods
    @abstractmethod
    def matrix(self):
        """ returns the matrix representation """
        pass

    def vector(self):
        """ returns the vector representation """
        pass

    def inverse(self):
        """ returns the inverted group element """
        pass

    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix):
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_vector(cls, vector):
        """ generates group element from vector """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args, **kwargs):
        """ generates group element from vector elements """
        pass

    @staticmethod
    @abstractmethod
    def vector_to_algebra(vector):
        """ returns the algebra corresponding to the vector """
        pass

    @staticmethod
    @abstractmethod
    def algebra_to_vector(algebra):
        """ returns the vector corresponding to the algebra """
        pass
