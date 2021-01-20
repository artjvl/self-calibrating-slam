from abc import ABC, abstractmethod


class Group(ABC):

    # constructor
    def __init__(self, vector):
        self._vector = vector

    # operators
    def __mul__(self, other):
        matrix = self.matrix()
        product = matrix*other
        return self.from_matrix(product)

    # public methods
    def vector(self):
        return self._vector

    def matrix(self):
        return self.vector_to_matrix(self.vector())

    # public class-methods
    @classmethod
    def from_vector(cls, vector):
        return cls(vector)

    @classmethod
    def from_matrix(cls, matrix):
        return cls(cls.matrix_to_vector(matrix))

    # abstract methods
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
