import typing as tp

from src.framework.graph.Graph import SubGraph

SubGraphContainer = tp.TypeVar('SubGraphContainer', bound='GraphContainer')


class GraphContainer(object):

    _graph: SubGraph  # original graph
    _graphs: tp.Dict[int, SubGraph]  # indexed subgraphs

    def __init__(self, graph: SubGraph):
        self._graph = graph
        self.index_graph()

    def index_graph(self) -> None:
        subgraphs: tp.List[SubGraph] = self._graph.subgraphs()
        keys: tp.List[tp.Optional[int]] = [subgraph.timestep() for subgraph in subgraphs]
        if any(timestep is None for timestep in keys) or \
                (len(keys) > 1 and len(set(keys)) == 1):
            keys = list(range(len(keys)))

        self._graphs = {keys[i]: subgraph for i, subgraph in enumerate(subgraphs)}

    def get_graphs(self) -> tp.List[SubGraph]:
        return [self._graphs[key] for key in sorted(self._graphs)]

    def get_graph(self, timestep: tp.Optional[int] = None) -> SubGraph:
        if timestep is None:
            return self.get_graphs()[-1]
        assert timestep in self._graphs
        return self._graphs[timestep]

    def is_singular(self) -> bool:
        # return not self.get_graph().has_previous()
        return len(self.get_timesteps()) == 1

    def has_timestep(self, timestep: int) -> bool:
        return timestep in self._graphs

    def get_timesteps(self) -> tp.List[int]:
        return sorted(self._graphs.keys())

    # subgraphs
    def find_subgraphs(self) -> None:
        if not self._graph.has_previous():
            self._graph.find_subgraphs()
        self.index_graph()

    # superset
    def is_superset(self, other: SubGraphContainer) -> bool:
        return set(self.get_timesteps()) >= set(other.get_timesteps())

    def is_superset_similar(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            timestep: int = other.get_timesteps()[-1]
            return self.get_graph(timestep).is_similar(other.get_graph(timestep))
        return False

    def is_superset_equivalent(self, other: SubGraphContainer) -> bool:
        if self.is_superset(other):
            timestep: int = other.get_timesteps()[-1]
            return self.get_graph(timestep).is_equivalent(other.get_graph(timestep))
        return False

    def is_superset_equal(self, other: SubGraphContainer) -> bool:
        is_superset: bool = self.is_superset(other)
        if is_superset:
            timestep: int = other.get_timesteps()[-1]
            return self.get_graph(timestep).is_equal(other.get_graph(timestep))
        return False
