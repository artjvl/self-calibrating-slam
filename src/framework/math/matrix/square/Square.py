import typing as tp

import numpy as np
from scipy import linalg

from src.framework.math.Dimensional import Dimensional
from src.framework.math.matrix.Matrix import Matrix, SubMatrix, List2D

SubSquare = tp.TypeVar('SubSquare', bound='Square', covariant=True)


class Square(Matrix, Dimensional):

    def __init__(
            self,
            data: tp.Union[List2D, np.ndarray]
    ):
        square: np.ndarray = np.asarray(data).astype(float)
        assert square.ndim == 2
        assert square.shape[0] == square.shape[1] == self.dim()
        super().__init__(square)

    # alternative representations
    def diagonal(self) -> tp.List[float]:
        return self._matrix.diagonal().tolist()

    # manipulations
    def inverse(self) -> SubSquare:
        return type(self)(np.linalg.pinv(self._matrix))

    def sqrt(self) -> SubSquare:
        return type(self)(linalg.sqrtm(self._matrix))

    # alternative creators
    @classmethod
    def zeros(cls) -> SubMatrix:
        dim = cls.dim()
        return cls(np.zeros((dim, dim)))

    @classmethod
    def ones(cls) -> SubMatrix:
        dim = cls.dim()
        return cls(np.ones((dim, dim)))

    @classmethod
    def identity(cls) -> SubMatrix:
        return cls(np.eye(cls.dim()))

    @classmethod
    def from_diagonal(cls, list_: tp.List[float]) -> SubMatrix:
        return cls(np.diag(list_))
