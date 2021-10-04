import typing as tp

from src.framework.graph.Graph import Graph

if tp.TYPE_CHECKING:
    from src.framework.graph.Graph import SubGraph, SubNode, SubEdge

SubGraphManager = tp.TypeVar('SubGraphManager', bound='GraphManager')


class GraphManager(object):

    # graph
    _graph: 'SubGraph'

    # counters
    _id_counter: int
    _id_set: tp.Set[int]
    _timestep: int

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._graph = Graph()

        # counters
        self._id_counter = 0
        self._id_set = set()
        self._timestep = 0

    # graph
    def graph(self) -> 'SubGraph':
        return self._graph

    # elements
    def add_node(
            self,
            node: 'SubNode',
            id_: tp.Optional[int] = None
    ) -> 'SubNode':
        if id_ is not None:
            # check if node-id has not been used before
            assert id_ not in self._id_set
            self._id_set.add(id_)
        else:
            # use default node-id
            id_ = self.get_id(should_increment=True)

        node.set_id(id_)
        node.set_timestep(self._timestep)
        self._graph.add_node(node)
        return node

    def get_node(self, id_: int) -> 'SubNode':
        """ Returns a node. """
        return self._graph.get_node(id_)

    def add_edge(self, edge: 'SubEdge') -> 'SubEdge':
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

    # timestep
    def set_timestep(self, timestep: int = 0) -> None:
        assert timestep >= self._timestep
        self._timestep = timestep

    def increment_timestep(self, delta: int = 1) -> None:
        self.set_timestep(self._timestep + delta)

    def get_timestep(self) -> int:
        return self._timestep
