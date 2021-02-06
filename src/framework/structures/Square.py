import numpy as np
from scipy import linalg


class Square(np.ndarray):

    # constructor
    def __new__(cls, elements):
        array = np.asarray(elements)
        assert len(array.shape) == 2
        assert array.shape[0] == array.shape[1]
        return array.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # public methods
    def inverse(self):
        return type(self)(linalg.inv(self))

    # public class-methods
    @classmethod
    def zeros(cls, size):
        return cls(np.zeros((size, size)))
