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
        def _array_to_string(array):
            assert isinstance(array, (list, np.ndarray))
            return ' '.join([str(float('{:.5e}'.format(element))) for element in array.flatten()])

        @classmethod
        def _symmetric_to_string(cls, matrix):
            assert isinstance(matrix, Square)
            elements = []
            indices = np.arange(matrix.shape[0])
            for i in indices:
                for j in indices[i:]:
                    elements.append(matrix[i][j])
            return cls._array_to_string(np.array(elements))

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
        def __init__(self, nodes, value):
            assert isinstance(nodes, list)
            assert all(isinstance(node, FactorGraph.Node) for node in nodes)
            assert isinstance(value, (Vector, SO, SE))
            super().__init__(nodes)
            self._value = value

        # public methods
        def get_value(self):
            return self._value

        def set_value(self, value):
            assert isinstance(value, (Vector, SO, SE))
            self._value = value

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

    # sub-class: Constraint
    class Constraint(Edge, ABC):

        # constructor
        def __init__(self, nodes, value, information):
            assert isinstance(nodes, list)
            assert all(isinstance(node, FactorGraph.Node) for node in nodes)
            assert isinstance(value, (Vector, SO, SE))
            assert isinstance(information, Square)
            super().__init__(nodes, value)
            self._information = information

        # public methods
        def get_information(self):
            return self._information

        def set_information(self, information):
            assert isinstance(information, Square)
            self._information = information

    # constructor
    def __init__(self):
        super().__init__()
