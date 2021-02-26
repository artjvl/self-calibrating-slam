import numpy as np

from src.framework.groups.SE import SE
from src.framework.groups.SO3 import SO3
from src.framework.structures import *


class SE3(SE[SO3]):
    # reference: https://github.com/utiasSTARS/liegroups

    # static properties
    _dim = 3
    _dof = 3
    _rotation_type = SO3

    # constructor
    def __init__(self, translation: Vector, rotation: SO3):
        super().__init__(translation, rotation)

    # alternative representations
    def quaternion_vector(self) -> Vector:
        translation = self.translation()
        quaternion = self.rotation().quaternion()
        return Vector(np.vstack((translation, quaternion)))

    def euler_vector(self) -> Vector:
        translation = self.translation()
        euler = self.rotation().euler()
        return Vector(np.vstack((translation, euler)))

    # alternative constructors
    @classmethod
    def from_elements(cls, x: float, y: float, z: float, a: float, b: float, c: float):
        translation_vector = Vector([x, y, z])
        rotation_vector = Vector([a, b, c])
        return cls.from_vectors(translation_vector, rotation_vector)

    @classmethod
    def from_quaternion(cls, translation: Vector, quaternion: Quaternion):
        rotation = SO3.from_quaternion(quaternion)
        return cls(translation, rotation)

    @classmethod
    def from_euler(cls, translation: Vector, euler: Vector):
        rotation = SO3.from_euler(euler)
        return cls(translation, rotation)

    # helper-methods
    @staticmethod
    def _vector_to_algebra(vector: Vector) -> Square:
        x = vector.get(0)
        y = vector.get(1)
        z = vector.get(2)
        a = vector.get(3)
        b = vector.get(4)
        c = vector.get(5)
        return Square([[0, -c, b, x],
                       [c, 0, -a, y],
                       [-b, a, 0, z],
                       [0, 0, 0, 0]])

    @staticmethod
    def _algebra_to_vector(algebra: Square) -> Vector:
        return Vector([algebra[0, 3],
                       algebra[1, 3],
                       algebra[2, 3],
                       algebra[2, 1],
                       algebra[0, 2],
                       algebra[1, 0]])
