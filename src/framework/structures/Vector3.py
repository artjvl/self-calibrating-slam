from __future__ import annotations
import numpy as np
from typing import *

from src.framework.structures.Vector import Vector
from src.framework.structures.Vector2 import Vector2


class Vector3(Vector):

    # constructor
    def __new__(cls, elements: Union[Tuple[float, ...], List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        assert len(column) == 3
        super().__new__(cls, elements)

    # operators
    def __xor__(self, other) -> Vector3:
        return type(self)(np.cross(self, other))

    # getters
    def x(self) -> float:
        return self.get(0)

    def y(self) -> float:
        return self.get(1)

    def z(self) -> float:
        return self.get(2)

    # public methods
    def split(self) -> Tuple[Vector2, float]:
        return Vector2(self[0:2]), self.get(3)

    # alternative constructor
    @classmethod
    def from_elements(cls, x: float, y: float, z: float) -> Vector3:
        return cls([x, y, z])
