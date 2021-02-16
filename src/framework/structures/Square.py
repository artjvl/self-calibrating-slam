from __future__ import annotations
import numpy as np
from scipy import linalg
from typing import *


class Square(np.ndarray):

    # constructor
    def __new__(cls, array: Union[List[List[float]], np.ndarray]):
        array = np.asarray(array)
        assert len(array.shape) == 2
        assert array.shape[0] == array.shape[1]
        return array.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    # object methods
    def __getitem__(self, key):
        sub = super().__getitem__(key)
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

    # alternative constructors
    @classmethod
    def zeros(cls, dimension: int) -> Square:
        return cls(np.zeros((dimension, dimension)))
