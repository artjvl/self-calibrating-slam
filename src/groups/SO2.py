import numpy as np

from src.structures import *
from src.groups.SO import SO


class SO2(SO):

    # static properties
    _dim = 2
    _dof = 1

    # constructor
    def __init__(self, matrix):
        assert isinstance(matrix, Square)
        super().__init__(matrix)

    # public methods
    def angle(self):
        return self.vector()[0][0]

    def smallest_angle(self):
        return self.smallest_positive_angle() - np.pi

    def smallest_positive_angle(self):
        return self.angle() % (2 * np.pi)

    # abstract implementations
    @classmethod
    def from_elements(cls, angle):
        vector = Vector(angle)
        return cls(vector)

    def left_jacobian(self):
        angle = self.angle()
        if np.isclose(angle, 0.):
            return Square(np.eye(type(self)._dim) + 0.5 * type(self).vector_to_algebra(self.vector()))
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)
        return (1/angle)*Square([[sin_angle, cos_angle - 1],
                                 [1 - cos_angle, sin_angle]])

    @classmethod
    def algebra_to_matrix(cls, algebra):
        assert isinstance(algebra, Square)
        vector = cls.algebra_to_vector(algebra)
        return cls.vector_to_matrix(vector)

    @classmethod
    def vector_to_matrix(cls, vector):
        assert isinstance(vector, Vector)
        angle = vector[0][0]
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)
        return Square(np.array([[cos_angle, -sin_angle],
                                [sin_angle, cos_angle]]))

    @classmethod
    def algebra_to_vector(cls, algebra):
        assert isinstance(algebra, Square)
        return Vector(algebra[1][0])

    @classmethod
    def matrix_to_algebra(cls, matrix):
        assert isinstance(matrix, Square)
        vector = cls.matrix_to_vector(matrix)
        return cls.vector_to_algebra(vector)

    @classmethod
    def matrix_to_vector(cls, matrix):
        assert isinstance(matrix, Square)
        return Vector(np.arctan2(matrix[1][0], matrix[0][0]))

    @staticmethod
    def elements():
        return list([Square([[0, -1], [1, 0]])])
