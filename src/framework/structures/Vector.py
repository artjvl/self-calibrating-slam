from __future__ import annotations

from typing import *

import numpy as np
from scipy import linalg

from src.framework.structures.Square import Square


class Vector(np.ndarray):

    # constructor
    def __new__(cls, elements: Union[float, Tuple[float, ...], List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        return column.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    def __str__(self):
        return np.array2string(self, precision=3, suppress_small=True)

    # public methods
    def get(self, index: int) -> float:
        assert index < len(self)
        return self[index, 0]

    def set(self, index: int, value: float):
        assert index < len(self)
        self[index] = value

    def insert(self, element: Optional[float] = 0., index: Optional[int] = -1) -> Vector:
        lst = self.to_list()
        if index < 0 or index >= len(lst):
            lst.append(element)
        else:
            lst.insert(index, element)
        return self.from_list(lst)

    def extend(self, element: Optional[float] = 0.) -> Vector:
        return self.insert(element, -1)

    def magnitude(self) -> float:
        return linalg.norm(self)

    def normal(self) -> Vector:
        magnitude = self.magnitude()
        if np.isclose(magnitude, 0.):
            unit = type(self).zeros(self.get_dimension())
            unit.set(0, 1.)
            return type(self)(unit)
        return self / magnitude

    def get_dimension(self) -> int:
        return self.shape[0]

    # alternative representations
    def to_1d(self) -> np.ndarray:
        return self.flatten()

    def to_list(self) -> List[float]:
        return list(self.to_1d())

    def to_tuple(self) -> Tuple[float, ...]:
        return tuple(self.to_list())

    def to_diagonal(self) -> Square:
        return Square(np.diag(self.to_1d()))

    # alternative constructors
    @classmethod
    def from_elements(cls, *args) -> Vector:
        return cls(args)

    @classmethod
    def from_list(cls, lst: List[float]) -> Vector:
        return cls(lst)

    @classmethod
    def from_array(cls, array: np.ndarray) -> Vector:
        return cls(array)

    @classmethod
    def zeros(cls, dimension: int) -> Vector:
        return cls(np.zeros((dimension, 1)))
