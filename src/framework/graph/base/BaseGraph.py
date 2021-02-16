from __future__ import annotations
from typing import *
import warnings

from src.framework.graph.base.BaseNode import BaseNode
from src.framework.graph.base.BaseEdge import BaseEdge

N = TypeVar('N', bound=BaseNode)
E = TypeVar('E', bound=BaseEdge)


class BaseGraph(Generic[N, E], object):

    # constructor
    def __init__(self):
        self._nodes: Dict[int, N] = dict()
        self._edges: List[E] = list()
        self._nodes_sorted: Dict[Type[N], List[N]] = dict()
        self._edges_sorted: Dict[Type[E], List[E]] = dict()

    # public methods
    def get_nodes(self) -> List[N]:
        return list(self._nodes.values())

    def get_node(self, id: int) -> N:
        assert id in self._nodes
        return self._nodes[id]

    def get_node_types(self) -> List[Type[N]]:
        return list(self._nodes_sorted.keys())

    def get_nodes_of_type(self, node_type: Type[N]) -> List[N]:
        assert node_type in self._nodes_sorted
        return self._nodes_sorted[node_type]

    def add_node(self, node: N):
        if node.id() in self._nodes:
            warnings.warn('Node with id {} already present in Graph {}'.format(node.id(), self))
        self._nodes[node.id()] = node
        node_type = type(node)
        if node_type not in self._nodes_sorted:
            self._nodes_sorted[node_type] = list()
        self._nodes_sorted[node_type].append(node)

    def get_edges(self) -> List[E]:
        return self._edges

    def get_edge(self, index: int) -> E:
        assert index < len(self._edges)
        return self._edges[index]

    def get_edge_types(self) -> List[Type[E]]:
        return list(self._edges_sorted.keys())

    def get_edges_of_type(self, edge_type: Type[E]) -> List[E]:
        assert edge_type in self._edges_sorted
        return self._edges_sorted[edge_type]

    def add_edge(self, edge: E):
        assert all(node in self._nodes.values() for node in edge.get_nodes())
        if edge in self._edges:
            warnings.warn('{} already present in Graph {}'.format(edge, self))
        else:
            self._edges.append(edge)
            edge_type = type(edge)
            if edge_type not in self._edges_sorted:
                self._edges_sorted[edge_type] = list()
            self._edges_sorted[edge_type].append(edge)

    # object methods
    def __str__(self) -> str:
        node_string = ', '.join(['{}: {}'.format(key.__name__, len(value)) for key, value in self._nodes_sorted.items()])
        edge_string = ', '.join(['{}: {}'.format(key.__name__, len(value)) for key, value in self._edges_sorted.items()])
        return '{}({})'.format(self.__class__.__name__, '; '.join(list(filter(lambda s: s != '', [node_string, edge_string]))))

    def __repr__(self) -> str:
        return '{} <at {}>'.format(str(self), hex(id(self)))
