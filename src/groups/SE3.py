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

    @classmethod
    def algebra_to_matrix(cls, algebra):
        assert isinstance(algebra, Square)

    @classmethod
    def vector_to_matrix(cls, vector):
        assert isinstance(vector, Vector)

    @classmethod
    def algebra_to_vector(cls, algebra):
        assert isinstance(algebra, Square)

    @classmethod
    def matrix_to_algebra(cls, matrix):
        assert isinstance(matrix, Square)

    @classmethod
    def matrix_to_vector(cls, matrix):
        assert isinstance(matrix, Square)
