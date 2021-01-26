import numpy as np

from src.structures import *
from src.groups.SO3 import SO3
from src.groups.SE import SE


class SE3(SE):

    # static properties
    _dim = 3
    _dof = 3
    _rotation_type = SO3

    # constructor
    def __init__(self, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO3)
        super().__init__(translation, rotation)

    # public methods
    def quaternion_vector(self):
        translation = self.translation()
        quaternion = self.rotation().quaternion()
        return Vector(np.vstack((translation, quaternion)))

    # abstract implementations
    @classmethod
    def from_elements(cls, x, y, z, a, b, c):
        translation_vector = Vector([x, y, z])
        rotation_vector = Vector([a, b, c])
        return cls.from_vectors(translation_vector, rotation_vector)

    @classmethod
    def from_quaternion(cls, quaternion, translation):
        assert isinstance(quaternion, Quaternion)
        assert isinstance(translation, Vector)
        rotation = SO3.from_quaternion(quaternion)
        return cls(translation, rotation)

    @staticmethod
    def vector_to_algebra(vector):
        assert isinstance(vector, Vector)
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
    def algebra_to_vector(algebra):
        assert isinstance(algebra, Square)
        return Vector([algebra[0][3],
                       algebra[1][3],
                       algebra[2][3],
                       algebra[2][1],
                       algebra[0][2],
                       algebra[1][0]])
