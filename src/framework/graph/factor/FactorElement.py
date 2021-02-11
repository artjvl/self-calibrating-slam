import numpy as np
from abc import ABC, abstractmethod
from typing import *

from src.framework.structures import *
from src.framework.groups import *


class FactorElement(ABC):

    # constructor
    def __init__(self, value: Union[Vector, SO, SE], **kwargs):
        super().__init__(**kwargs)
        self._value = value

    # public methods
    def get_value(self) -> Union[Vector, SO, SE]:
        return self._value

    def set_value(self, value: Union[Vector, SO, SE]):
        self._value = value

    # helper-methods
    @staticmethod
    def _array_to_lst(array: np.ndarray) -> List[float]:
        return list(array.flatten())

    @staticmethod
    def _lst_to_string(elements: List[float]) -> str:
        elements = [float('{:.5e}'.format(element)) for element in elements]
        for i, element in enumerate(elements):
            if element.is_integer():
                elements[i] = int(element)
        return ' '.join(str(element) for element in elements)
        # return ' '.join([str(float('{:.5e}'.format(element))) for element in elements])

    @classmethod
    def _symmetric_to_lst(cls, matrix: Square) -> List[float]:
        elements = []
        indices = np.arange(matrix.shape[0])
        for i in indices:
            for j in indices[i:]:
                elements.append(matrix[i][j])
        return elements

    @classmethod
    def _lst_to_symmetric(cls, elements: List[float]) -> Square:
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
