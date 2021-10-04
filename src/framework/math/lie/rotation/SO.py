import typing as tp
from abc import abstractmethod

import numpy as np

from src.framework.math.lie.Lie import SubLie, Lie
from src.framework.math.matrix.square import SubSquare, SquareFactory
from src.framework.math.matrix.vector import SubVector, VectorFactory

SubSO = tp.TypeVar('SubSO', bound='SO')


class SO(Lie):
    _matrix: SubSquare

    def __init__(
            self,
            matrix: SubSquare
    ):
        super().__init__()
        self._matrix = matrix

    # properties
    @classmethod
    def get_size(cls) -> int:
        return cls.dim()

    def inverse(self) -> SubLie:
        square: SubSquare = SquareFactory.from_dim(self.dim())(np.transpose(self.array()))
        return type(self)(square)

    @abstractmethod
    def angle(self) -> float:
        pass

    @abstractmethod
    def jacobian(self) -> SubSquare:
        """ returns the left Jacobian of the group element """
        pass

    @abstractmethod
    def inverse_jacobian(self) -> SubSquare:
        """ returns the inverse left Jacobian of the group element """
        pass

    # alternative representations
    def matrix(self) -> SubSquare:
        return self._matrix

    # alternative creators
    @classmethod
    def from_elements(cls, *args: float) -> SubLie:
        assert len(args) == cls.get_dof()
        vector: SubVector = VectorFactory.from_dim(cls.get_dof())(args)
        return cls.from_vector(vector)

    @classmethod
    def from_matrix(cls, matrix: SubSquare) -> SubLie:
        return cls(matrix)
