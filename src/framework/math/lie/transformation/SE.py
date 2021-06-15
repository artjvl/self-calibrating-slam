import typing as tp
from abc import ABC

import numpy as np

from src.framework.math.lie.Lie import Lie
from src.framework.math.lie.rotation.SO import SubSO
from src.framework.math.lie.rotation.SOFactory import SOFactory
from src.framework.math.matrix.square import SubSquare, SquareFactory
from src.framework.math.matrix.vector import SubVector, VectorFactory

SubSE = tp.TypeVar('SubSE', bound='SE')


class SE(Lie, ABC):

    def __init__(
            self,
            translation: SubVector,
            rotation: SubSO
    ):
        self._translation = translation
        self._rotation = rotation

    # operators
    def oplus(self, vector: SubVector):
        increment: SubSE = type(self).from_vector(vector)
        return self + increment

    def ominus(self, transformation: SubSE) -> SubVector:
        difference: SubSE = self - transformation
        return difference.vector()

    # properties
    @classmethod
    def get_size(cls) -> int:
        return cls.get_dim() + 1

    def translation(self) -> SubVector:
        return self._translation

    def rotation(self) -> SubSO:
        return self._rotation

    def inverse(self) -> SubSE:
        inverse_rotation: SubSO = self.rotation().inverse()
        inverse_translation: SubVector = VectorFactory.from_dim(self.get_dim())(
            - inverse_rotation.array() @ self.translation().array()
        )
        return type(self)(inverse_translation, inverse_rotation)

    # alternative representations
    def matrix(self) -> SubSquare:
        return self._construct_matrix(self.translation(), self.rotation())

    def vector(self) -> SubVector:
        dof: int = self.get_dof()
        return VectorFactory.from_dim(dof)(
            np.vstack((self.translation_vector().array(), self.rotation_vector().array()))
        )

    def rotation_vector(self) -> SubVector:
        return self.rotation().vector()

    def translation_vector(self) -> SubVector:
        dim: int = self.get_dim()
        return VectorFactory.from_dim(dim)(
            self.rotation().inverse_jacobian().array() @ self.translation().array()
        )

    # alternative creators
    @classmethod
    def from_matrix(
            cls,
            matrix: SubSquare
    ) -> SubSE:
        translation: SubVector = cls._extract_translation(matrix)
        rotation: SubSO = cls._extract_rotation(matrix)
        return cls(translation, rotation)

    @classmethod
    def from_vectors(
            cls,
            translation_vector: SubVector,
            rotation_vector: SubVector
    ) -> SubSE:
        dim: int = cls.get_dim()
        rotation: SubSO = SOFactory.from_dim(dim).from_vector(rotation_vector)
        jacobian: SubSquare = rotation.jacobian()
        translation: SubVector = VectorFactory.from_dim(dim)(
            jacobian.array() @ translation_vector.array()
        )
        return cls(translation, rotation)

    @classmethod
    def from_vector(
            cls,
            vector: SubVector
    ) -> SubSE:
        dim: int = cls.get_dim()
        dof: int = cls.get_dof()
        translation_vector: SubVector = VectorFactory.from_dim(dim)(vector[:dim])
        rotation_vector: SubVector = VectorFactory.from_dim(dof - dim)(vector[dim:])
        return cls.from_vectors(translation_vector, rotation_vector)

    @classmethod
    def from_elements(cls, *args: float) -> SubSE:
        assert len(args) == cls.get_dof()
        vector: SubVector = VectorFactory.from_dim(cls.get_dof())(args)
        return cls.from_vector(vector)

    # helper-methods
    @classmethod
    def _construct_matrix(
            cls,
            translation: SubVector,
            rotation: SubSO
    ) -> SubSquare:
        pad_array = np.zeros((1, cls.get_dim()))
        matrix_array = np.block([[rotation.array(), translation.array()],
                                 [pad_array, 1]])

        size: int = cls.get_size()
        square: SubSquare = SquareFactory.from_dim(size)(matrix_array)
        return square

    @classmethod
    def _extract_translation(
            cls,
            matrix: SubSquare
    ) -> SubVector:
        dim: int = cls.get_dim()
        return VectorFactory.from_dim(dim)(matrix[: dim, dim:])

    @classmethod
    def _extract_rotation(
            cls,
            matrix: SubSquare
    ) -> SubSO:
        dim: int = cls.get_dim()
        matrix = SquareFactory.from_dim(dim)(matrix[: dim, : dim])
        return SOFactory.from_dim(dim).from_matrix(matrix)
