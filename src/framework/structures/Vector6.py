from __future__ import annotations
import numpy as np
from typing import *

from src.framework.structures.Vector import Vector
from src.framework.structures.Vector3 import Vector3


class Vector6(Vector):

    # constructor
    def __new__(cls, elements: Union[Tuple[float, ...], List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        assert len(column) == 6
        super().__new__(cls, elements)

    # getters
    def x(self) -> float:
        return self.get(0)

    def y(self) -> float:
        return self.get(1)

    def z(self) -> float:
        return self.get(2)

    def a(self) -> float:
        return self.get(3)

    def b(self) -> float:
        return self.get(4)

    def c(self) -> float:
        return self.get(5)

    # public methods
    def split(self) -> Tuple[Vector3, Vector3]:
        return Vector3(self[0:3]), Vector3(self[3:6])

    # alternative constructor
    @classmethod
    def from_elements(cls, x: float, y: float, z: float, a: float, b: float, c: float) -> Vector6:
        return cls([x, y, z, a, b, c])
