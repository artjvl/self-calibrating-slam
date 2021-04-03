from __future__ import annotations

import typing
import warnings

import numpy as np
from scipy import linalg

from src.framework.structures.MultiDimensional import MultiDimensional

SubVector = typing.TypeVar('SubVector', bound='Vector')


class Vector(np.ndarray, MultiDimensional):

    dim: typing.Optional[int] = None

    # constructor
    def __new__(
            cls,
            *args: typing.Any
    ):
        column: np.ndarray
        if np.shape(args[0]):
            column = np.reshape(args[0], (-1, 1))
        else:
            column = np.reshape(args, (-1, 1))
        return column.astype(float).view(cls)

    def __array_finalize__(self, obj):
        # assert self.shape[1] == 1
        if obj is None:
            return

    def __str__(self):
        return np.array2string(self, precision=3, suppress_small=True)

    def get_dimension(self) -> int:
        return self.shape[0]

    # getter/setter methods
    def get(self, index: int) -> float:
        assert index < len(self)
        return self[index, 0]

    def set(self, index: int, value: float):
        assert index < len(self)
        self[index] = value

    # modification
    def insert(
            self,
            element: typing.Optional[float] = 0.,
            index: typing.Optional[int] = -1
    ) -> Vector:
        lst: typing.List[float] = self.to_list()
        if index < 0 or index >= len(lst):
            lst.append(element)
        else:
            lst.insert(index, element)
        return Vector.from_list(lst)

    def extend(
            self,
            element: typing.Optional[float] = 0.
    ) -> Vector:
        return Vector.insert(self, element, -1)

    # manipulation
    def sqrt(self) -> SubVector:
        return type(self)(np.sqrt(self))

    def magnitude(self) -> float:
        return float(linalg.norm(self))

    def normal(self) -> SubVector:
        magnitude = self.magnitude()
        if np.isclose(magnitude, 0.):
            unit = type(self).zeros(self.get_dimension())
            unit.set(0, 1.)
            return type(self)(unit)
        return self / magnitude

    # alternative representations
    def to_1d(self) -> np.ndarray:
        return np.array(self.flatten())

    def to_list(self) -> typing.List[float]:
        return list(self.to_1d())

    def to_tuple(self) -> typing.Tuple[float, ...]:
        return tuple(self.to_list())

    # alternative constructors
    @classmethod
    def from_elements(cls, *args: float) -> SubVector:
        return cls(args)

    @classmethod
    def from_list(cls, lst: typing.List[float]) -> SubVector:
        return cls(lst)

    @classmethod
    def from_array(cls, array: np.ndarray) -> SubVector:
        return cls(array)

    @classmethod
    def zeros(cls, dimension: typing.Optional[int] = None) -> SubVector:
        if cls.dim is not None:
            if dimension is not None:
                warnings.warn(f'<dimension={dimension}> is not used.')
            return cls(np.zeros((cls.dim, 1)))
        else:
            assert dimension is not None
            return Vector(np.zeros((dimension, 1)))

    @classmethod
    def ones(cls, dimension: typing.Optional[int] = None) -> SubVector:
        if cls.dim is not None:
            if dimension is not None:
                warnings.warn(f'<dimension={dimension}> is not used.')
            return cls(np.zeros((cls.dim, 1)))
        else:
            assert dimension is not None
            return Vector(np.ones((dimension, 1)))
