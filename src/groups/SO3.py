import numpy as np

from src.structures import *
from src.groups.SO import SO


class SO3(SO):

    # static properties
    _dim = 3
    _dof = 3

    # constructor
    def __init__(self, matrix):
        assert isinstance(matrix, Square)
        super().__init__(matrix)

    # public methods
    def angle(self):
        return self.vector().magnitude()

    # abstract implementations
    @classmethod
    def from_elements(cls, r1, r2, r3):
        vector = Vector([r1, r2, r3])
        return cls(vector)

    def left_jacobian(self):
        vector = self.vector()
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            return Square(np.eye(3) + 0.5 * type(self).vector_to_algebra(self.vector()))
        unit = vector.normal()
        unit_algebra = type(self).vector_to_algebra(unit)
        matrix = np.eye(3) + unit_algebra*(1 - np.cos(angle)) + (unit_algebra**2)*(1 - np.sin(angle)/angle)
        return Square(matrix)

    @classmethod
    def algebra_to_matrix(cls, algebra):
        assert isinstance(algebra, Square)
        vector = cls.algebra_to_vector(algebra)
        return cls.vector_to_matrix(vector)

    @classmethod
    def vector_to_matrix(cls, vector):
        assert isinstance(vector, Vector)
        angle = vector.magnitude()
        unit = vector.normal()
        unit_algebra = cls.vector_to_algebra(unit)

        # Rodrigues formula
        matrix = np.eye(3) + unit_algebra*np.sin(angle) + (unit_algebra**2)*(1 - np.cos(angle))
        return Square(matrix)

    @classmethod
    def algebra_to_vector(cls, algebra):
        assert isinstance(algebra, Square)
        return Vector([algebra[2][1],
                       algebra[0][2],
                       algebra[1][0]])

    @classmethod
    def matrix_to_algebra(cls, matrix):
        assert isinstance(matrix, Square)
        angle = np.arccos(0.5*(np.trace(matrix) - 1))
        if np.isclose(angle, 0.):
            return matrix - np.eye(3)
        return (angle*(matrix - np.transpose(matrix)))/(2*np.sin(angle))

    @classmethod
    def matrix_to_vector(cls, matrix):
        assert isinstance(matrix, Square)
        return cls.algebra_to_vector(cls.matrix_to_algebra(matrix))

    @staticmethod
    def elements():
        return list([Square([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
                     Square([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
                     Square([[0, -1, 0], [1, 0, 0], [0, 0, 0]])])
