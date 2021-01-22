import numpy as np
from abc import ABC, abstractmethod
from enum import Enum

from src.structures import *
from src.groups.Group import Group
from src.groups.SO2 import SO2
from src.groups.SO3 import SO3


class SO(Group, ABC, Enum):

    # enums
    SO2 = SO2
    SO3 = SO3

    # constructor
    def __init__(self, vector, matrix=None):
        assert isinstance(vector, Vector)
        super().__init__(vector, matrix)

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        # number of dimensions
        pass

    @property
    @abstractmethod
    def m(self):
        # number of degrees of freedom
        pass

    # abstract methods
    @staticmethod
    @abstractmethod
    def elements():
        # returns the list of base elements
        pass

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = Square(np.zeros((cls.n, cls.n)))
        for index in range(cls.m):
            algebra += vector[index] * elements[index]
        return algebra
