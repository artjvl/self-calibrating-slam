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
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO2)
        super().__init__(translation, rotation)

    # abstract implementations
    @classmethod
    def from_elements(cls, x, y, a):
        translation_vector = Vector([x, y])
        rotation_vector = Vector(a)
        return cls.from_vectors(translation_vector, rotation_vector)

    @staticmethod
    def vector_to_algebra(vector):
        assert isinstance(vector, Vector)
        x = vector.get(0)
        y = vector.get(1)
        a = vector.get(2)
        return Square([[0, -a, x],
                       [a, 0, y],
                       [0, 0, 0]])

    @staticmethod
    def algebra_to_vector(algebra):
        assert isinstance(algebra, Square)
        return Vector([algebra[0][2],
                       algebra[1][2],
                       algebra[1][0]])
