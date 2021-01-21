from abc import ABC, abstractmethod
from src.structures import *
from src.groups.Group import Group


class SO(Group, ABC):

    # constructor
    def __init__(self, vector):
        assert isinstance(vector, Vector)
        super().__init__(vector)

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        pass

    @property
    @abstractmethod
    def m(self):
        pass

    # abstract methods
    @staticmethod
    @abstractmethod
    def elements():
        pass

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = Square(np.zeros((n, n)))
        for index in range(m):
            algebra += vector[index] * elements[index]
        return algebra
