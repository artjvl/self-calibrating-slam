import numpy as np
from scipy import linalg
from typing import *


class Vector(np.ndarray):

    # constructor
    def __new__(cls, elements):
        column = np.reshape(elements, (-1, 1))
        return column.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    def __str__(self):
        return np.array2string(self, precision=3, suppress_small=True)

    # public methods
    def get(self, index):
        return self[index][0]

    def magnitude(self):
        return self.norm(self)

    def normal(self):
        return self.unit(self)

    def to_lst(self):
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
            return cls.from_lst(unit)
        return vector / magnitude

    def insert(self, element: Optional[float] = 0., index: Optional[int] = -1):
        lst = self.to_lst()
        if index < 0 or index >= len(lst):
            lst.append(element)
        else:
            lst.insert(index, element)
        return self.from_lst(lst)

    def extend(self, element: Optional[float] = 0.):
        return self.insert(element, -1)

    # alternative constructors
    @classmethod
    def from_lst(cls, lst):
        assert isinstance(lst, (list, np.ndarray))
        return cls(lst)

    @classmethod
    def zeros(cls, dimension):
        return cls(np.zeros((dimension, 1)))
