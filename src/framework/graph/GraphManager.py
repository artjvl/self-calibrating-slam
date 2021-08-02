import typing as tp
from src.framework.graph.Graph import SubGraph, SubNode, SubEdge

SubGraphManager = tp.TypeVar('SubGraphManager', bound='GraphManager')


class GraphManager(object):

    _graph: SubGraph
    _counter: int
    _timestamp: float

    def __init__(self, graph: SubGraph):
        self._graph = graph
        self._counter = 0
        self._timestamp = 0.

    # graph
    def get_graph(self) -> SubGraph:
        return self._graph

    # elements
    def add_node(self, node: SubNode) -> None:
        node.set_id(self.get_count(increment=True))
        node.set_timestamp(self._timestamp)
        self._graph.add_node(node)

    def add_edge(self, edge: SubEdge) -> None:
        self._graph.add_edge(edge)

    # count
    def get_count(self, increment: bool = False) -> int:
        count: int = self._counter
        if increment:
            self._counter += 1
        return count

    def set_count(self, count: int) -> None:
        assert count >= self._counter
        self._counter = count

    # timestamp
    def set_timestamp(self, timestamp: float) -> None:
        assert timestamp > self._timestamp
        self._timestamp = timestamp

    def increment_timestamp(self, delta: float) -> None:
        self.set_timestamp(self._timestamp + delta)
