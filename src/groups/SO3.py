import numpy as np
from scipy import linalg
from .SO import SO


class SO3(SO):

    # static properties
    n = 3

    # constructor
    def __init__(self, vector):
        super().__init__(vector)

    # private class-methods
    @classmethod
    def _vector_to_angle(cls, vector):
        return linalg.norm(vector)

    @classmethod
    def _vector_to_unit(cls, vector):
        return vector/cls._vector_to_angle(vector)

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        elements = [np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
                    np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
                    np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]])]
        return vector[0]*elements[0] + vector[1]*elements[1] + vector[2]*elements[2]

    @classmethod
    def algebra_to_matrix(cls, algebra):
        vector = cls.algebra_to_vector(algebra)
        return cls.vector_to_matrix(vector)

    @classmethod
    def vector_to_matrix(cls, vector):
        angle = cls._vector_to_angle(vector)
        unit = cls._vector_to_unit(vector)
        unit_algebra = cls.vector_to_algebra(unit)

        # Rodrigues formula
        return np.eye(3) + unit_algebra*np.sin(angle) + (unit_algebra**2)*(1 - np.cos(angle))

    @classmethod
    def algebra_to_vector(cls, algebra):
        return np.array([[algebra[2][1]],
                         [algebra[0][2]],
                         [algebra[1][0]]])

    @classmethod
    def matrix_to_algebra(cls, matrix):
        angle = np.arccos(0.5*(np.trace(matrix) - 1))
        return (angle*(matrix - np.transpose(matrix)))/(2*np.sin(angle))

    @classmethod
    def matrix_to_vector(cls, matrix):
        return cls.algebra_to_vector(cls.matrix_to_algebra(matrix))
