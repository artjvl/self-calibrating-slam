import numpy as np
from .SO import SO


class SO2(SO):

    # static properties
    n = 2

    # constructor
    def __init__(self, angle):
        super().__init__(angle)

    # public methods
    def angle(self):
        return self.vector()

    def smallest_angle(self):
        return self.smallest_positive_angle() - np.pi

    def smallest_positive_angle(self):
        return self.angle() % (2 * np.pi)

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        element = np.array([[0, -1],
                            [1, 0]])
        return vector*element

    @classmethod
    def algebra_to_matrix(cls, algebra):
        vector = cls.algebra_to_vector(algebra)
        return cls.vector_to_matrix(vector)

    @classmethod
    def vector_to_matrix(cls, vector):
        sin_angle = np.sin(vector)
        cos_angle = np.cos(vector)
        return np.array([[cos_angle, -sin_angle],
                         [sin_angle, cos_angle]])

    @classmethod
    def algebra_to_vector(cls, algebra):
        return algebra[1][0]

    @classmethod
    def matrix_to_algebra(cls, matrix):
        vector = cls.matrix_to_vector(matrix)
        return cls.vector_to_algebra(vector)

    @classmethod
    def matrix_to_vector(cls, matrix):
        # assert isinstance(matrix, np.ndarray)
        # assert matrix.shape == (2, 2)
        return np.arctan2(matrix[1][0], matrix[0][0])
