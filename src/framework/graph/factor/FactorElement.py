from abc import ABC, abstractmethod
from typing import *

import numpy as np

from src.framework.structures import *

T = TypeVar('T')


class FactorElement(Generic[T], ABC):

    # constructor
    def __init__(self, value: T, **kwargs):
        super().__init__(**kwargs)
        self._value = value

    # public methods
    def get_value(self) -> T:
        return self._value

    def set_value(self, value: T):
        self._value = value

    # helper-methods
    @staticmethod
    def _array_to_list(array: np.ndarray) -> List[float]:
        return list(array.flatten())

    @staticmethod
    def _list_to_string(elements: List[float]) -> str:
        elements = [float('{:.5e}'.format(element)) for element in elements]
        for i, element in enumerate(elements):
            if element.is_integer():
                elements[i] = int(element)
        return ' '.join(str(element) for element in elements)
        # return ' '.join([str(float('{:.5e}'.format(element))) for element in elements])

    @classmethod
    def _symmetric_to_list(cls, matrix: Square) -> List[float]:
        elements = []
        indices = np.arange(matrix.shape[0])
        for i in indices:
            for j in indices[i:]:
                elements.append(matrix[i][j])
        return elements

    @classmethod
    def _list_to_symmetric(cls, elements: List[float]) -> Square:
        length = len(elements)
        dimension = -0.5 + 0.5 * np.sqrt(1 + 8 * length)
        assert dimension.is_integer()
        dimension = int(dimension)
        matrix = Square.zeros(dimension)
        indices = np.arange(dimension)
        count = 0
        for i in indices:
            for j in indices[i:]:
                matrix[i, j] = elements[count]
                matrix[j, i] = matrix[i, j]
                count += 1
        return matrix

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def tag(cls):
        pass

    # abstract methods
    @abstractmethod
    def write(self):
        pass

    @classmethod
    @abstractmethod
    def read(cls, words):
        pass
