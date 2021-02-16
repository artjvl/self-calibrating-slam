from typing import *
import warnings

from src.framework.graph.base.BaseNode import BaseNode
from src.framework.graph.base.BaseEdge import BaseEdge

N = TypeVar('N', bound=BaseNode)
E = TypeVar('E', bound=BaseEdge)


class BaseGraph(Generic[N, E], object):

    # constructor
    def __init__(self):
        self._nodes = dict()
        self._edges = list()

    # public methods
    def get_nodes(self) -> List[N]:
        return list(self._nodes.values())

    def get_node(self, id: int) -> N:
        assert id in self._nodes
        return self._nodes[id]

    def add_node(self, node: N):
        if node.id() in self._nodes:
            warnings.warn('Node with id {} already present in Graph {}'.format(node.id(), self))
        self._nodes[node.id()] = node

    def get_edges(self) -> List[E]:
        return self._edges

    def get_edge(self, index: int) -> E:
        assert index < len(self._edges)
        return self._edges[index]

    def add_edge(self, edge: E):
        assert all(node in self._nodes.values() for node in edge.get_nodes())
        if edge in self._edges:
            warnings.warn('{} already present in Graph {}'.format(edge, self))
        else:
            self._edges.append(edge)

    # helper-methods
    @staticmethod
    def _count_types(lst: list) -> str:
        types = dict()
        for element in lst:
            if type(element) not in types:
                types[type(element)] = 0
            types[type(element)] += 1
        return ', '.join(['{}: {}'.format(key.__name__, types[key]) for key in types.keys()])

    # object methods
    def __str__(self) -> str:
        node_types = self._count_types(list(self.get_nodes()))
        edge_types = self._count_types(list(self.get_edges()))
        return '{}({})'.format(self.__class__.__name__, '; '.join(list(filter(lambda s: s != '', [node_types, edge_types]))))

    def __repr__(self) -> str:
        return '{} <at {}>'.format(str(self), hex(id(self)))
