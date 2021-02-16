from __future__ import annotations
import numpy as np
from typing import *

from src.framework.structures.Vector import Vector


class Vector2(Vector):

    # constructor
    def __new__(cls, elements: Union[Tuple[float, ...], List[float], np.ndarray]):
        column = np.reshape(elements, (-1, 1))
        assert len(column) == 2
        super().__new__(cls, elements)

    # getters
    def x(self) -> float:
        return self.get(0)

    def y(self) -> float:
        return self.get(1)

    # alternative constructor
    @classmethod
    def from_elements(cls, x: float, y: float) -> Vector2:
        return cls([x, y])
