import typing as tp

import numpy as np

from src.framework.structures import Square


class Parser(object):

    # data to words
    @staticmethod
    def array_to_list(array: np.ndarray) -> tp.List[float]:
        return list(array.flatten())

    @staticmethod
    def symmetric_to_list(matrix: Square) -> tp.List[float]:
        elements = []
        indices = np.arange(matrix.shape[0])
        for i in indices:
            for j in indices[i:]:
                elements.append(matrix[i][j])
        return elements

    @staticmethod
    def list_to_words(elements: tp.List[float]) -> tp.List[str]:
        elements = [float('{:.5e}'.format(element)) for element in elements]
        for i, element in enumerate(elements):
            if element.is_integer():
                elements[i] = int(element)
        return [f'{element}' for element in elements]

    # words to data
    @staticmethod
    def words_to_list(words: tp.List[str]) -> tp.List[float]:
        return [float(word) for word in words]

    @classmethod
    def list_to_symmetric(cls, elements: tp.List[float]) -> Square:
        length = len(elements)
        dimension = -0.5 + 0.5 * np.sqrt(1 + 8 * length)
        assert dimension.is_integer(), f'elements {elements} are not divisible to form a symmetric matrix of dimension {dimension})'
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
