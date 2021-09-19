import typing as tp

from src.framework.graph.Graph import SubGraph

SubGraphContainer = tp.TypeVar('SubGraphContainer', bound='GraphContainer')


class GraphContainer(object):

    _graph: SubGraph  # original graph
    _graphs: tp.Dict[float, SubGraph]  # indexed subgraphs

    def __init__(self, graph: SubGraph):
        self._graph = graph
        self.index_graph()

    def index_graph(self) -> None:
        subgraphs: tp.List[SubGraph] = self._graph.get_subgraphs()
        keys: tp.List[tp.Optional[float]] = [subgraph.get_timestamp() for subgraph in subgraphs]
        if any(timestamp is None for timestamp in keys) or \
                (len(keys) > 1 and len(set(keys)) == 1):
            keys = list(range(len(keys)))

        self._graphs = {keys[i]: subgraph for i, subgraph in enumerate(subgraphs)}

    def get_graphs(self) -> tp.List[SubGraph]:
        return [self._graphs[key] for key in sorted(self._graphs)]

    def get_graph(self, timestamp: tp.Optional[float] = None) -> SubGraph:
        if timestamp is None:
            return self.get_graphs()[-1]
        assert timestamp in self._graphs
        return self._graphs[timestamp]

    def is_singular(self) -> bool:
        # return not self.get_graph().has_previous()
        return len(self.get_timestamps()) == 1

    def has_timestamp(self, timestamp: float) -> bool:
        return timestamp in self._graphs

    def get_timestamps(self) -> tp.List[float]:
        return sorted(self._graphs.keys())

    # subgraphs
    def find_subgraphs(self) -> None:
        if not self._graph.has_previous():
            self._graph.find_subgraphs()
        self.index_graph()

    # superset
    def is_superset(self, other: SubGraphContainer) -> bool:
        return set(self.get_timestamps()) >= set(other.get_timestamps())

    def is_superset_similar(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            timestamp: float = other.get_timestamps()[-1]
            return self.get_graph(timestamp).is_similar(other.get_graph(timestamp))
        return False

    def is_superset_equivalent(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            timestamp: float = other.get_timestamps()[-1]
            return self.get_graph(timestamp).is_equivalent(other.get_graph(timestamp))
        return False

    def is_superset_equal(self, other: SubGraphContainer) -> bool:
        is_superset: bool = self.is_superset(other)
        if is_superset:
            timestamp: float = other.get_timestamps()[-1]
            return self.get_graph(timestamp).is_equal(other.get_graph(timestamp))
        return False
