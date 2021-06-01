import typing as tp
from abc import abstractmethod

import numpy as np

SubMatrix = tp.TypeVar('SubMatrix', bound='Matrix', covariant=True)


class Matrix(object):

    def __init__(
            self,
            matrix: np.ndarray
    ):
        self._matrix: np.ndarray = matrix

    # alternative representations
    def array(self) -> np.ndarray:
        return self._matrix

    # access
    def __getitem__(self, item):
        return self._matrix[item]

    def __setitem__(self, key, value) -> None:
        self._matrix[key] = value

    # alternative creators
    @classmethod
    @abstractmethod
    def zeros(cls) -> SubMatrix:
        pass

    @classmethod
    @abstractmethod
    def ones(cls) -> SubMatrix:
        pass

    def to_string(
            self,
            precision: tp.Optional[int] = None,
            suppress_small: bool = False
    ) -> str:
        return np.array2string(self.array(), precision=precision, suppress_small=suppress_small)

    # print
    def __str__(self):
        return self.to_string(
            precision=3,
            suppress_small=True
        )

    def __repr__(self):
        name: str = self.__class__.__name__
        return name + np.array2string(
            self.array(),
            prefix=name
        )
