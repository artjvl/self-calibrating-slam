import numpy as np


class SO2(object):
    def __init__(self, angle):
        self._n = 2
        self._angle = angle

    def angle(self):
        return self._angle

    def to_matrix(self):
        return self.find_matrix(self._angle)

    def smallest_angle(self):
        return  self.smallest_positive_angle() - np.pi

    def smallest_positive_angle(self):
        return self._angle % (2*np.pi)

    # def set_angle(self, angle):
    #     self._angle = angle
    #
    # def set_matrix(self, matrix):
    #     self.set_angle(self.find_angle(matrix))

    @classmethod
    def find_matrix(cls, angle):
        sin_angle = np.sin(angle)
        cos_angle = np.cos(angle)
        return np.array([[cos_angle, -sin_angle],
                         [sin_angle, cos_angle]])

    @classmethod
    def find_angle(cls, matrix):
        # assert isinstance(matrix, np.ndarray)
        # assert matrix.shape == (2, 2)
        return np.arctan2(matrix[1][0], matrix[0][0])

    @classmethod
    def from_angle(cls, angle):
        return cls(angle)

    @classmethod
    def from_matrix(cls, matrix):
        return cls(cls.find_angle(matrix))
