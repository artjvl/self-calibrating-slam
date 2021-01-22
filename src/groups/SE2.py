import numpy as np
from src.structures import *
from src.groups.SO2 import SO2
from src.groups.SE import SE

class SE2(SE):

    # static properties
    n = 2
    m = 1

    # constructor
    def __init__(self, translation, rotation):
        assert isinstance(translation, Vector2)
        assert isinstance(rotation, SO2)
        super().__init__(translation, rotation)

    # abstract implementations
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
