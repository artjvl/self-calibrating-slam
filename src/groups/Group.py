from abc import ABC, abstractmethod

from src.structures import *


class Group(ABC):

    # operators
    def __mul__(self, other):
        product = self.matrix() * other.matrix()
        return self.from_matrix(product)

    # public methods
    def vector(self):
        """ returns the vector representation """
        return self.matrix_to_vector(self.matrix())

    # public class-methods
    @classmethod
    def from_vector(cls, vector):
        """ generates group element from vector """
        assert isinstance(vector, Vector)
        matrix = cls.matrix_to_vector(vector)
        return cls.from_matrix(matrix)

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def _dim(cls):
        """ number of dimensions """
        pass

    @property
    @classmethod
    @abstractmethod
    def _dof(cls):
        """ number of degrees of freedom """
        pass

    # abstract methods
    @abstractmethod
    def matrix(self):
        """ returns the matrix representation """
        pass

    @classmethod
    @abstractmethod
    def from_matrix(cls, matrix):
        """ generates group element from matrix """
        pass

    @classmethod
    @abstractmethod
    def from_elements(cls, *args, **kwargs):
        """ generates group element from vector elements """
        pass

    @classmethod
    @abstractmethod
    def vector_to_algebra(cls, vector):
        """ 'hat' operator """
        pass

    @classmethod
    @abstractmethod
    def algebra_to_matrix(cls, algebra):
        """ 'exp' operator """
        pass

    @classmethod
    @abstractmethod
    def vector_to_matrix(cls, vector):
        """ 'Exp' operator """
        pass

    @classmethod
    @abstractmethod
    def algebra_to_vector(cls, algebra):
        """ 'vee' operator """
        pass

    @classmethod
    @abstractmethod
    def matrix_to_algebra(cls, matrix):
        """ 'log' operator """
        pass

    @classmethod
    @abstractmethod
    def matrix_to_vector(cls, matrix):
        """ 'Log' operator """
        pass
