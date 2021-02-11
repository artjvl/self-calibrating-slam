import numpy as np
from scipy import linalg
from typing import *


class Square(np.ndarray):

    # constructor
    def __new__(cls, elements: List):
        array = np.asarray(elements)
        assert len(array.shape) == 2
        assert array.shape[0] == array.shape[1]
        return array.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # object methods
    def __getitem__(self, item):
        sub = super().__getitem__(item)
        if len(sub.shape) == 1:
            return np.array(sub)
        elif len(sub.shape) == 2 and sub.shape[0] != sub.shape[1]:
            return np.array(sub)
        return sub

    def __str__(self) -> str:
        return np.array2string(self, precision=3, suppress_small=True)

    # public methods
    def inverse(self):
        return type(self)(linalg.inv(self))

    # public class-methods
    @classmethod
    def zeros(cls, dimension):
        return cls(np.zeros((dimension, dimension)))
