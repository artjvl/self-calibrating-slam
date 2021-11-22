import typing as tp

from src.framework.graph.Graph import SubGraph

SubGraphContainer = tp.TypeVar('SubGraphContainer', bound='GraphContainer')


class GraphContainer(object):

    _graph: 'SubGraph'  # original graph
    _graphs: tp.List['SubGraph']  # indexed subgraphs

    def __init__(self, graph: 'SubGraph'):
        self._graphs = graph.subgraphs()

    def get_graphs(self) -> tp.List['SubGraph']:
        return self._graphs

    def get_graph(self, index: tp.Optional[int] = None) -> 'SubGraph':
        if index is None:
            return self._graphs[-1]
        return self._graphs[index]

    def is_singular(self) -> bool:
        # return not self.get_graph().has_previous()
        return len(self._graphs) == 1

    def has_timestep(self, timestep: int) -> bool:
        return timestep in self._graphs

    def get_timesteps(self) -> tp.List[int]:
        return [graph.timestep() for graph in self._graphs]

    def last_graph_with_timestep(self, timestep: int) -> 'SubGraph':
        indices: tp.List[int] = [i for i, _ in enumerate(self.get_timesteps()) if i == timestep]
        return self.get_graph(indices[-1])

    # subgraphs
    def find_subgraphs(self) -> None:
        graph: 'SubGraph' = self.get_graph()
        assert self.is_singular() and not graph.has_previous()
        graph.find_subgraphs()
        self._graphs = graph.subgraphs()

    # superset
    def is_superset(self, other: SubGraphContainer) -> bool:
        return set(self.get_timesteps()) >= set(other.get_timesteps())

    def is_superset_similar(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            other_graph: 'SubGraph' = other.get_graphs()[-1]
            self_graph: 'SubGraph' = self.last_graph_with_timestep(other_graph.timestep())
            return self_graph.is_similar(other_graph)
        return False

    def is_superset_equivalent(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            other_graph: 'SubGraph' = other.get_graphs()[-1]
            self_graph: 'SubGraph' = self.last_graph_with_timestep(other_graph.timestep())
            return self_graph.is_equivalent(other_graph)
        return False

    def is_superset_equal(self, other: SubGraphContainer) -> bool:
        is_superset: bool = self.is_superset(other)
        if is_superset:
            other_graph: 'SubGraph' = other.get_graphs()[-1]
            self_graph: 'SubGraph' = self.last_graph_with_timestep(other_graph.timestep())
            return self_graph.is_equal(other_graph)
        return False
