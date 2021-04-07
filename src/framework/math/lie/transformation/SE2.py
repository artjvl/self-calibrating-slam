from __future__ import annotations

import typing as tp

from src.framework.math.lie.rotation.SO2 import SO2
from src.framework.math.lie.transformation import SE3
from src.framework.math.lie.transformation.SE import SE
from src.framework.math.matrix.square import SubSquare, Square3
from src.framework.math.matrix.vector import SubVector, Vector2, Vector3


class SE2(SE):

    _dim = 2
    _dof = 3

    def __init__(
            self,
            translation: Vector2,
            rotation: SO2
    ):
        super().__init__(translation, rotation)

    # alternative representations
    def translation_angle(self) -> tp.Tuple[Vector2, float]:
        return self.translation(), self.rotation().angle()

    def translation_angle_vector(self) -> Vector3:
        return Vector3(*(self.translation().to_list()), self.rotation().angle())

    def translation_angle_list(self) -> tp.List[float]:
        return self.translation().to_list() + [self.rotation().angle()]

    # conversion
    def to_se3(self) -> SE3:
        return SE3(self.translation().to_vector3(), self.rotation().to_so3())

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: SubVector) -> SubSquare:
        x: float = vector[0]
        y: float = vector[1]
        a: float = vector[2]
        return Square3([[0, -a, x],
                        [a, 0, y],
                        [0, 0, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: SubSquare) -> SubVector:
        return Vector3([algebra[0, 2],
                        algebra[1, 2],
                        algebra[1, 0]])

    # alternative creators:
    @classmethod
    def from_translation_angle(
            cls,
            translation: Vector2,
            angle: float
    ) -> SE2:
        return cls(translation, SO2.from_angle(angle))

    @classmethod
    def from_translation_angle_elements(
            cls,
            x: float,
            y: float,
            angle: float
    ) -> SE2:
        return cls(Vector2(x, y), SO2.from_angle(angle))

    @classmethod
    def from_translation_angle_vector(
            cls,
            translation_angle_vector: Vector3
    ) -> SE2:
        list_: tp.List[float] = translation_angle_vector.to_list()
        return cls(Vector2(list_[0], list_[1]), SO2.from_angle(list_[2]))
