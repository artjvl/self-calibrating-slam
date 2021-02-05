import numpy as np
from abc import ABC, abstractmethod


class Element(ABC):

    # private static-methods
    @staticmethod
    def _array_to_string(array):
        assert isinstance(array, np.ndarray)
        return ' '.join(['{:.6f}'.format(element) for element in array.flatten()])

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def tag(cls):
        pass

    # abstract methods
    @abstractmethod
    def to_string(self):
        pass

    @classmethod
    @abstractmethod
    def read(cls, words):
        pass
