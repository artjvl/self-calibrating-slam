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
        return self.vector().get(0)

    def smallest_angle(self):
        return self.smallest_positive_angle() - np.pi

    def smallest_positive_angle(self):
        return self.angle() % (2 * np.pi)

    # abstract implementations
    def vector(self):
        matrix = self.matrix()
        return Vector(np.arctan2(matrix[1][0], matrix[0][0]))

    def jacobian(self):
        angle = self.angle()
        if np.isclose(angle, 0.):
            return Square(np.eye(2) + 0.5 * self.algebra())
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)
        matrix = (1 / angle) * Square([[sin_angle, cos_angle - 1],
                                       [1 - cos_angle, sin_angle]])
        return Square(matrix)

    def inverse_jacobian(self):
        jacobian = self.jacobian()
        a = jacobian[0][0]
        b = jacobian[1][0]
        matrix = (1 / (a**2 + b**2)) * Square([[a, b],
                                               [-b, a]])
        return Square(matrix)

    @classmethod
    def from_vector(cls, vector):
        assert isinstance(vector, Vector)
        angle = vector[0][0]
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)
        matrix = [[cos_angle, -sin_angle],
                  [sin_angle, cos_angle]]
        return cls(Square(matrix))

    @classmethod
    def from_elements(cls, angle):
        assert isinstance(angle, (int, float))
        vector = Vector(angle)
        return cls.from_vector(vector)

    @staticmethod
    def vector_to_algebra(vector):
        assert isinstance(vector, Vector)
        a = vector.get(0)
        return Square([[0, -a],
                       [a, 0]])

    @staticmethod
    def algebra_to_vector(algebra):
        assert isinstance(algebra, Square)
        return Vector(algebra[1][0])
