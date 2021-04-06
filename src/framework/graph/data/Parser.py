import typing as tp

import numpy as np

from src.framework.math.matrix.square import SubSquare, SquareFactory


class Parser(object):

    # data to words
    @classmethod
    def symmetric_to_list(cls, matrix: SubSquare) -> tp.List[float]:
        elements: tp.List[float] = []
        indices = np.arange(matrix.shape[0])
        for i in indices:
            for j in indices[i:]:
                elements.append(matrix[i][j])
        return elements

    @staticmethod
    def array_to_list(array: np.ndarray) -> tp.List[float]:
        return list(array.flatten())

    @staticmethod
    def list_to_words(elements: tp.List[float]) -> tp.List[str]:
        words: tp.List[str] = []
        for element in elements:
            element = float('{:.5f}'.format(element))
            if element.is_integer():
                word = str(int(element))
            else:
                word = str(element)
            words.append(word)
        return words

    # words to data
    @classmethod
    def list_to_symmetric(cls, elements: tp.List[float]) -> SubSquare:
        length = len(elements)
        dimension = -0.5 + 0.5 * np.sqrt(1 + 8 * length)
        assert dimension.is_integer(), \
            f'elements {elements} are not divisible to form a symmetric matrix ({dimension})'
        dimension = int(dimension)
        matrix = SquareFactory.from_dim(dimension).zeros()

        indices = np.arange(dimension)
        count: int = 0
        for i in indices:
            for j in indices[i:]:
                matrix[i, j] = elements[count]
                matrix[j, i] = matrix[i, j]
                count += 1
        return matrix

    @staticmethod
    def words_to_list(words: tp.List[str]) -> tp.List[float]:
        return [float(word) for word in words]
