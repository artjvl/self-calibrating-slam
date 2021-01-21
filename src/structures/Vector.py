import numpy as np
from scipy import linalg


class Vector(np.ndarray):

    # constructor
    def __new__(cls, elements):
        column = np.reshape(elements, (-1, 1))
        obj = np.asarray(column).view(cls)
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # public methods
    def magnitude(self):
        return self.norm(self)

    def normal(self):
        return self.unit(self)

    # public class-methods
    @classmethod
    def norm(cls, vector):
        return linalg.norm(vector)

    @classmethod
    def unit(cls, vector):
        magnitude = cls.norm(vector)
        if np.isclose(magnitude, 0.):
            unit = np.zeros((vector.size, 1))
            unit[0] = 1
            return unit
        return vector / magnitude
