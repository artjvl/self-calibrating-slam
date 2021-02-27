from __future__ import annotations

import warnings
from typing import *

from src.framework.graph.base.BaseEdge import BaseEdge
from src.framework.graph.base.BaseElement import BaseElement
from src.framework.graph.base.BaseNode import BaseNode

N = TypeVar('N', bound=BaseNode)
E = TypeVar('E', bound=BaseEdge)


class BaseGraph(Generic[N, E], BaseElement):

    def __init__(self):
        self._nodes: Dict[int, N] = {}
        self._edges: List[E] = []
        self._nodes_sorted: Dict[Type[N], List[N]] = {}
        self._edges_sorted: Dict[Type[E], List[E]] = {}

    def id_string(self):
        node_string: str = ', '.join(
            ['{}: {}'.format(key.__name__, len(value)) for key, value in self._nodes_sorted.items()]
        )
        edge_string: str = ', '.join(
            ['{}: {}'.format(key.__name__, len(value)) for key, value in self._edges_sorted.items()]
        )
        return '; '.join(list(filter(lambda s: s != '', [node_string, edge_string])))

    # node methods
    def add_node(self, node: N) -> None:
        if node.get_id() in self._nodes:
            warnings.warn('Node with id {} already present in Graph {}'.format(node.get_id(), self))
        self._nodes[node.get_id()] = node

        # sorting
        node_type: Type[N] = type(node)
        if node_type not in self._nodes_sorted:
            self._nodes_sorted[node_type] = []
        self._nodes_sorted[node_type].append(node)

    def get_nodes(self) -> List[N]:
        return list(self._nodes.values())

    def get_node(self, id: int) -> N:
        assert id in self._nodes, '{} in {}'.format(id, self._nodes)
        return self._nodes[id]

    def get_node_types(self) -> List[Type[N]]:
        return list(self._nodes_sorted.keys())

    def get_nodes_of_type(self, node_type: Type[N]) -> List[N]:
        assert node_type in self._nodes_sorted
        return self._nodes_sorted[node_type]

    # edge methods
    def add_edge(self, edge: E) -> None:
        assert all(node in self._nodes.values() for node in edge.get_nodes())
        if edge in self._edges:
            warnings.warn('{} already present in Graph {}'.format(edge, self))
        else:
            self._edges.append(edge)

            # sorting
            edge_type: Type[E] = type(edge)
            if edge_type not in self._edges_sorted:
                self._edges_sorted[edge_type] = []
            self._edges_sorted[edge_type].append(edge)

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

    # element methods
    def get_elements(self) -> List[Any]:
        return self.get_nodes() + self.get_edges()

    def get_element_types(self) -> List[Type[Any]]:
        return self.get_node_types() + self.get_edge_types()

    def get_elements_of_type(self, element_type: Type[Any]) -> List[Any]:
        if element_type in self.get_node_types():
            return self.get_nodes_of_type(element_type)
        elif element_type in self.get_edge_types():
            return self.get_edges_of_type(element_type)
