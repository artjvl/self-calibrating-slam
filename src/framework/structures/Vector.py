import numpy as np
from scipy import linalg


class Vector(np.ndarray):

    # constructor
    def __new__(cls, elements):
        column = np.reshape(elements, (-1, 1))
        return column.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # public methods
    def get(self, index):
        return self[index][0]

    def magnitude(self):
        return self.norm(self)

    def normal(self):
        return self.unit(self)

    def to_list(self):
        return list(self.flatten())

    # public class-methods
    @classmethod
    def norm(cls, vector):
        assert isinstance(vector, cls)
        return linalg.norm(vector)

    @classmethod
    def unit(cls, vector):
        assert isinstance(vector, cls)
        magnitude = cls.norm(vector)
        if np.isclose(magnitude, 0.):
            unit = np.zeros(vector.shape)
            unit[0] = 1
            return cls.from_list(unit)
        return vector / magnitude

    @classmethod
    def from_list(cls, elements):
        assert isinstance(elements, (list, np.ndarray))
        return cls(elements)

    # public static-methods
    @staticmethod
    def axes(size):
        axes = list()
        for index in range(size):
            axis = np.zeros(size, 1)
            axis[index] = 1
            axes.append(axis)
