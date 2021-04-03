from __future__ import annotations

from src.framework.structures.Vector import Vector


class Vector2(Vector):

    dim = 2

    # constructor
    def __array_finalize__(self, obj):
        assert self.get_dimension() == self.dim

    # getters
    def x(self) -> float:
        return self.get(0)

    def y(self) -> float:
        return self.get(1)

    # alternative constructor
    @classmethod
    def from_elements(cls, x: float, y: float) -> Vector2:
        return cls([x, y])
