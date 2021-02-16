import numpy as np
from scipy import linalg
from typing import *


class Vector(np.ndarray):

    # constructor
    def __new__(cls, elements: Union[float, List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        return column.view(cls)

    def __array_finalize__(self, obj):
        if obj is None:
            return

    def __str__(self):
        return np.array2string(self, precision=3, suppress_small=True)

    # public methods
    def get(self, index: int) -> float:
        return self[index, 0]

    def set(self, index: int, value: float):
        self[index] = value

    def insert(self, element: Optional[float] = 0., index: Optional[int] = -1):
        lst = self.to_lst()
        if index < 0 or index >= len(lst):
            lst.append(element)
        else:
            lst.insert(index, element)
        return self.from_lst(lst)

    def extend(self, element: Optional[float] = 0.):
        return self.insert(element, -1)

    def magnitude(self) -> float:
        return linalg.norm(self)

    def normal(self):
        magnitude = self.magnitude()
        if np.isclose(magnitude, 0.):
            unit = type(self).zeros(self.get_dimension())
            unit.set(0, 1.)
            return type(self)(unit)
        return self / magnitude

    def get_dimension(self):
        return self.shape[0]

    # alternative representations
    def to_lst(self) -> List[float]:
        return list(self.flatten())

    # alternative constructors
    @classmethod
    def from_lst(cls, lst: List[float]):
        return cls(lst)

    @classmethod
    def from_array(cls, array: np.ndarray):
        return cls(array)

    @classmethod
    def zeros(cls, dimension: int):
        return cls(np.zeros((dimension, 1)))
