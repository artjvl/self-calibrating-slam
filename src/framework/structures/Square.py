from __future__ import annotations

from typing import *

import numpy as np
from scipy import linalg

from src.framework.structures.MultiDimensional import MultiDimensional, Sub
from src.framework.structures.Vector import Vector


class Square(np.ndarray, MultiDimensional):

    # constructor
    def __new__(cls, array: Union[List[List[float]], np.ndarray]):
        array = np.asarray(array)
        assert len(array.shape) == 2
        assert array.shape[0] == array.shape[1]
        return array.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    def get_dimension(self) -> int:
        return self.shape[0]

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

    def diagonal(self) -> Vector:
        d = super().diagonal()
        v = Vector(d)
        return v
        # return Vector(super().diagonal())

    # alternative constructors
    @classmethod
    def zeros(cls, dimension: int) -> Square:
        return cls(np.zeros((dimension, dimension)))

    @classmethod
    def ones(cls, dimension: int) -> Sub:
        return cls(np.ones((dimension, dimension)))

    @classmethod
    def identity(cls, dimension: int) -> Square:
        return cls(np.eye(dimension))

    @classmethod
    def from_diagonal(cls, elements: List[float]) -> Square:
        return cls(np.diag(elements))
