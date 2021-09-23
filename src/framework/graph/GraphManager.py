import typing as tp

from src.framework.graph.CalibratingGraph import CalibratingGraph
from src.framework.graph.Graph import SubGraph, SubNode, SubEdge

SubGraphManager = tp.TypeVar('SubGraphManager', bound='GraphManager')


class GraphManager(object):

    # graph
    _graph: SubGraph

    # counters
    _id_counter: int
    _id_set: tp.Set[int]
    _timestamp: float

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._graph = CalibratingGraph()

        # counters
        self._id_counter = 0
        self._id_set = set()
        self._timestamp = 0.

    # graph
    def graph(self) -> SubGraph:
        return self._graph

    # elements
    def add_node(
            self,
            node: SubNode,
            id_: tp.Optional[int] = None
    ) -> SubNode:
        if id_ is not None:
            # check if node-id has not been used before
            assert id_ not in self._id_set
            self._id_set.add(id_)
        else:
            # use default node-id
            id_ = self.get_id(should_increment=True)

        node.set_id(id_)
        node.set_timestamp(self._timestamp)
        self._graph.add_node(node)
        return node

    def get_node(self, id_: int) -> 'SubNode':
        """ Returns a node. """
        return self._graph.get_node(id_)

    def add_edge(self, edge: SubEdge) -> SubEdge:
        self._graph.add_edge(edge)
        return edge

    # count
    def get_id(self, should_increment: bool = False) -> int:
        id_: int = self._id_counter
        if should_increment:
            self._id_set.add(id_)
            while self._id_counter in self._id_set:
                self._id_counter += 1
        return id_

    def set_count(self, count: int) -> None:
        assert count >= self._id_counter and count not in self._id_set
        self._id_counter = count

    # timestamp
    def set_timestamp(self, timestamp: float = 0.) -> None:
        assert timestamp >= self._timestamp
        self._timestamp = timestamp

    def increment_timestamp(self, delta: float) -> None:
        self.set_timestamp(self._timestamp + delta)

    def get_timestamp(self) -> float:
        return self._timestamp
