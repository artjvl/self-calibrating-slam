from __future__ import annotations

from typing import *

import numpy as np

from src.framework.structures.Vector import Vector


class Quaternion(Vector):

    # constructor
    def __new__(cls, elements: Union[Tuple[float, ...], List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        assert len(column) == 4
        super().__new__(cls, elements)

    # getters
    def w(self):
        return self.get(0)

    def x(self):
        return self.get(1)

    def y(self):
        return self.get(2)

    def z(self):
        return self.get(3)

    # alternative constructor
    @classmethod
    def from_elements(cls, w: float, x: float, y: float, z: float) -> Quaternion:
        return cls([w, x, y, z])
