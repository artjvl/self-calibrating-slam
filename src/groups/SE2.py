import numpy as np

from src.structures import *
from src.groups.SO2 import SO2
from src.groups.SE import SE


class SE2(SE):
    # static properties
    _dim = 2
    _dof = 1
    _rotation_type = SO2

    # constructor
    def __init__(self, translation, rotation):
        assert isinstance(translation, Vector2)
        assert isinstance(rotation, SO2)
        super().__init__(translation, rotation)

    # abstract implementations
    @classmethod
    def from_elements(cls, x, y, a):
        translation_vector = Vector([x, y])
        rotation_vector = Vector(a)
        return cls.from_vectors(translation_vector, rotation_vector)

    @staticmethod
    def elements():
        return list([Square([[0, 0, 1], [0, 0, 0], [0, 0, 0]]),
                     Square([[0, 0, 1], [0, 0, 1], [0, 0, 0]]),
                     Square([[0, -1, 0], [1, 0, 0], [0, 0, 0]])])
