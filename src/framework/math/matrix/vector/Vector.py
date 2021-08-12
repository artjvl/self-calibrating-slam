import typing as tp

import numpy as np
from scipy import linalg

from src.framework.math.Dimensional import Dimensional
from src.framework.math.matrix.Matrix import Matrix

SubVector = tp.TypeVar('SubVector', bound='Vector', covariant=True)
SubSizeVector = tp.TypeVar('SubSizeVector', bound='SizeVector', covariant=True)


class Vector(Matrix, Dimensional):

    def __init__(
            self,
            *args: tp.Any
    ):
        column: np.ndarray
        if np.shape(args[0]):
            column = np.reshape(args[0], (-1, 1))
        else:
            column = np.reshape(args, (-1, 1))
        vector = column.astype(float)
        super().__init__(vector)

    def get_length(self) -> int:
        return self.shape()[0]

    def __neg__(self) -> SubVector:
        return type(self)(- self.array())

    def __add__(self, other: SubVector) -> SubVector:
        assert type(other) == type(self)
        return type(self)(self.array() + other.array())

    def __sub__(self, other: SubVector) -> SubVector:
        assert type(other) == type(self)
        return type(self)(self.array() - other.array())

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._matrix[item, 0]
        return self._matrix[item]

    # manipulation
    def magnitude(self) -> float:
        return float(linalg.norm(self.array()))

    def normal(self) -> SubVector:
        magnitude: float = self.magnitude()
        if np.isclose(magnitude, 0.):
            unit: SubVector = self.zeros()
            unit[0] = 1.
            return unit
        return type(self)(self.array() / magnitude)

    # alternative representations
    def to_list(self) -> tp.List[float]:
        return list(self._matrix.flatten())


class SizeVector(Vector):

    _dim: int

    def __init__(
            self,
            *args: tp.Any
    ):
        super().__init__(args)
        assert self.array().shape[0] == self.get_dim()

    # alternative creators
    @classmethod
    def zeros(cls) -> SubVector:
        return cls(np.zeros((cls.get_dim(), 1)))

    @classmethod
    def ones(cls) -> SubVector:
        return cls(np.ones((cls.get_dim(), 1)))
