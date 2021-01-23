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
        assert isinstance(translation, Vector3)
        assert isinstance(rotation, SO3)
        super().__init__(translation, rotation)

    # abstract implementations
    @classmethod
    def from_elements(cls, x, y, z, a, b, c):
        translation_vector = Vector([x, y, z])
        rotation_vector = Vector([a, b, c])
        return cls.from_vectors(translation_vector, rotation_vector)

    @staticmethod
    def elements():
        return list([Square([[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
                     Square([[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]),
                     Square([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]),
                     Square([[0, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 0]]),
                     Square([[0, 0, 1, 0], [0, 0, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 0]]),
                     Square([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])])
