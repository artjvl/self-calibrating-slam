import numpy as np
from abc import ABC, abstractmethod

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.BaseGraph import BaseGraph


class FactorGraph(BaseGraph):

    # sub-class: Element
    class Element(ABC):

        # private static-methods
        @staticmethod
        def _array_to_elements(array):
            assert isinstance(array, np.ndarray)
            return list(array.flatten())

        @staticmethod
        def _elements_to_string(elements):
            elements = [float('{:.5e}'.format(element)) for element in elements]
            for i, element in enumerate(elements):
                if element.is_integer():
                    elements[i] = int(element)
            return ' '.join(str(element) for element in elements)
            # return ' '.join([str(float('{:.5e}'.format(element))) for element in elements])

        @classmethod
        def _symmetric_to_elements(cls, matrix):
            assert isinstance(matrix, Square)
            elements = []
            indices = np.arange(matrix.shape[0])
            for i in indices:
                for j in indices[i:]:
                    elements.append(matrix[i][j])
            return elements

        @classmethod
        def _elements_to_symmetric(cls, elements):
            assert isinstance(elements, list)
            assert all(isinstance(element, float) for element in elements)
            length = len(elements)
            dimension = -0.5 + 0.5 * np.sqrt(1 + 8 * length)
            assert dimension.is_integer()
            dimension = int(dimension)
            matrix = Square.zeros(dimension)
            indices = np.arange(dimension)
            count = 0
            for i in indices:
                for j in indices[i:]:
                    matrix[i][j] = elements[count]
                    matrix[j][i] = matrix[i][j]
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
        def to_string(self):
            pass

        @classmethod
        @abstractmethod
        def read(cls, words):
            pass

    # sub-class: Node
    class Node(BaseGraph.BaseNode, Element, ABC):

        # constructor
        def __init__(self, id, value):
            assert isinstance(id, int)
            assert isinstance(value, (Vector, SO, SE))
            super().__init__(id)
            self._value = value

        # public methods
        def get_value(self):
            return self._value

        def set_value(self, value):
            assert isinstance(value, (Vector, SO, SE))
            self._value = value

    # sub-class: Edge
    class Edge(BaseGraph.BaseEdge, Element, ABC):

        # constructor
        def __init__(self, nodes, value, information=None):
            assert isinstance(nodes, list)
            assert all(isinstance(node, FactorGraph.Node) for node in nodes)
            assert isinstance(value, (Vector, SO, SE))
            super().__init__(nodes)
            self._value = value
            if information is None:
                self._is_uncertain = False
            else:
                assert isinstance(information, Square)
                self._is_uncertain = True
            self._information = information

        # public methods
        def get_value(self):
            return self._value

        def set_value(self, value):
            assert isinstance(value, (Vector, SO, SE))
            self._value = value

        def is_uncertain(self):
            return self._is_uncertain

        def get_information(self):
            return self._information

        def set_information(self, information):
            assert isinstance(information, Square)
            self._information = information
            self._is_uncertain = True

        # abstract properties
        @property
        @classmethod
        @abstractmethod
        def size(cls):
            pass

        # abstract methods
        @classmethod
        @abstractmethod
        def from_nodes(cls, nodes):
            pass

    # constructor
    def __init__(self):
        super().__init__()
