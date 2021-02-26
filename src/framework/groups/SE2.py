import numpy as np

from src.framework.groups.SE import SE
from src.framework.groups.SE3 import SE3
from src.framework.groups.SO2 import SO2
from src.framework.structures import *


class SE2(SE[SO2]):
    # reference: https://github.com/utiasSTARS/liegroups

    # static properties
    _dim = 2
    _dof = 1
    _rotation_type = SO2

    # constructor
    def __init__(self, translation: Vector, rotation: SO2):
        super().__init__(translation, rotation)

    # public methods
    def to_se3(self) -> SE3:
        rotation = self.rotation()
        translation = self.translation()
        return SE3(Vector(np.vstack((translation, 0))), rotation.to_so3())

    # alternative constructors
    @classmethod
    def from_elements(cls, x: float, y: float, a: float):
        translation_vector = Vector([x, y])
        rotation_vector = Vector(a)
        return cls.from_vectors(translation_vector, rotation_vector)

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: Vector) -> Square:
        x = vector.get(0)
        y = vector.get(1)
        a = vector.get(2)
        return Square([[0, -a, x],
                       [a, 0, y],
                       [0, 0, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: Square) -> Vector:
        return Vector([algebra[0, 2],
                       algebra[1, 2],
                       algebra[1, 0]])
