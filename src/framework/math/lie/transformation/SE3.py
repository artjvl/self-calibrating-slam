from __future__ import annotations

from src.framework.math.lie.rotation.SO3 import SO3
from src.framework.math.lie.transformation.SE import SE
from src.framework.math.matrix.square import SubSquare, Square4
from src.framework.math.matrix.vector import SubVector, Vector3, Vector6


class SE3(SE):

    _dim = 3
    _dof = 6

    def __init__(
            self,
            translation: Vector3,
            rotation: SO3
    ):
        super().__init__(translation, rotation)

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: SubVector) -> SubSquare:
        x = vector[0]
        y = vector[1]
        z = vector[2]
        a = vector[3]
        b = vector[4]
        c = vector[5]
        return Square4([[0, -c, b, x],
                       [c, 0, -a, y],
                       [-b, a, 0, z],
                       [0, 0, 0, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: SubSquare) -> SubVector:
        return Vector6([algebra[0, 3],
                        algebra[1, 3],
                        algebra[2, 3],
                        algebra[2, 1],
                        algebra[0, 2],
                        algebra[1, 0]])
