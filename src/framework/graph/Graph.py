import pathlib
import typing as tp
from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.FactorGraph import FactorGraph, FactorNode, FactorEdge

if tp.TYPE_CHECKING:
    from src.framework.graph.protocols.Measurement import SubMeasurement
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector import SubVector

SubGraph = tp.TypeVar('SubGraph', bound='Graph')
SubNode = tp.TypeVar('SubNode', bound='Node')
SubEdge = tp.TypeVar('SubEdge', bound='Edge')
SubElement = tp.Union[SubNode, SubEdge]


class Graph(FactorGraph):

    # reference graphs
    _truth: tp.Optional[SubGraph]
    _pre: tp.Optional[SubGraph]

    # metadata
    _date: str
    _path: tp.Optional[pathlib.Path]
    _atol: tp.Optional[float]

    # properties
    _ate: tp.Optional[float]
    _rpe_translation: tp.Optional[float]
    _rpe_rotation: tp.Optional[float]

    def __init__(self):
        super().__init__()

        # reference graphs
        self._truth = None
        self._pre = None

        # metadata
        self._date = datetime.now().strftime('%Y%m%d-%H%M%S')
        self._path = None
        self._atol = 1e-6

        # metrics
        self.clear_metrics()

    def clear_metrics(self) -> None:
        super().clear_metrics()
        self._error = None
        self._ate = None
        self._rpe_translation = None
        self._rpe_rotation = None

    # properties
    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def has_path(self) -> bool:
        return self._path is not None

    def get_path(self) -> pathlib.Path:
        assert self.has_path()
        return self._path

    def get_pathname(self) -> str:
        assert self.has_path()
        return self._path.name

    def timestep(self) -> tp.Optional[int]:
        return self.get_nodes()[-1].get_timestep()

    # pre
    def has_pre(self) -> bool:
        return self._pre is not None

    def get_pre(self) -> SubGraph:
        assert self.has_pre()
        return self._pre

    def assign_pre(self, graph: SubGraph):
        assert self.is_equivalent(graph)
        self._pre = graph

    # metrics
    def get_ate(self) -> float:
        assert self.has_truth()
        if self._ate is None:
            te2: float = 0
            count: int = 0
            node: SubNode
            for node in self.get_nodes():
                node_ate2 = node.get_ate2()
                if node_ate2 is not None:
                    te2 += node_ate2
                    count += 1
            self._ate = np.sqrt(te2 / count)
        return self._ate

    def compute_ate(self) -> float:
        """ Returns the Absolute Trajectory Error (APE). """

        assert self.has_truth()
        te2: float = 0
        count: int = 0
        node: SubNode
        for node in self.get_nodes():
            node_ate2 = node.compute_ate2()
            if node_ate2 is not None:
                te2 += node_ate2
                count += 1
        self._ate = np.sqrt(te2/count)
        return self._ate

    def get_rpe_translation(self) -> float:
        assert self.has_truth()
        if self._rpe_translation is None:
            rpe2: float = 0
            count: int = 0
            edge: SubEdge
            for edge in self.get_edges():
                edge_rpe2 = edge.get_rpe_translation2()
                if edge_rpe2 is not None:
                    rpe2 += edge_rpe2
                    count += 1
            self._rpe_translation = np.sqrt(rpe2 / count)
        return self._rpe_translation

    def compute_rpe_translation(self) -> float:
        """ Returns the translation portion of the Relative Pose Error (RPE). """

        assert self.has_truth()
        rpe2: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_translation2()
            if edge_rpe2 is not None:
                rpe2 += edge_rpe2
                count += 1
        self._rpe_translation = np.sqrt(rpe2/count)
        return self._rpe_translation

    def get_rpe_rotation(self) -> float:
        assert self.has_truth()
        if self._rpe_rotation is None:
            rpe: float = 0
            count: int = 0
            edge: SubEdge
            for edge in self.get_edges():
                edge_rpe2 = edge.get_rpe_rotation2()
                if edge_rpe2 is not None:
                    rpe += edge_rpe2
                    count += 1
            self._rpe_rotation = rpe / count
        return self._rpe_rotation

    def compute_rpe_rotation(self) -> float:
        """ Returns the rotation portion of the Relative Pose Error (RPE). """

        assert self.has_truth()
        rpe: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_rotation2()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        self._rpe_rotation = rpe/count
        return self._rpe_rotation

    # truth
    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubGraph:
        assert self.has_truth()
        return self._truth

    def set_atol(self, atol: float) -> None:
        self._atol = atol

    def is_perturbed(self) -> bool:
        return not np.isclose(self.get_error(), 0., atol=self._atol)

    def assign_truth(
            self,
            graph: SubGraph
    ) -> None:
        """
        Populates the 'truth' (or ground-truth) reference with <graph>.
        Assumption: 'truth' graph only contains endpoints and shall be a subset of this graph.
        """
        assert not graph.is_perturbed()
        assert self.is_similar(graph)
        assert not self.has_truth()
        self._truth = graph

        # nodes
        id_: int
        for id_ in graph.get_node_ids():
            if self.contains_node_id(id_):
                node: SubNode = self.get_node(id_)
                truth_node: SubNode = graph.get_node(id_)
                node.assign_truth(truth_node)

        # edges
        edge_iter: iter = iter(self.get_edges())
        edge: tp.Optional[SubEdge] = None
        truth_edge: SubEdge
        for i, truth_edge in enumerate(graph.get_edges()):
            is_eligible: bool = False
            while not is_eligible:
                edge = next(edge_iter, None)
                assert edge is not None
                is_eligible = edge.is_eligible_for_truth(truth_edge)
            edge.assign_truth(truth_edge)

        # previous graphs
        if self.has_previous():
            self.find_truth_subgraphs()

    # subgraphs
    def find_subgraphs(self) -> None:
        super().find_subgraphs()

        # assigning timesteps to all nodes
        subgraphs: tp.List[SubGraph] = self.subgraphs()
        node_set: tp.Set[SubNode] = set()
        next_set: tp.Set[SubNode]
        for i, subgraph in enumerate(subgraphs):
            next_set = set(subgraph.get_nodes())

            node: SubNode
            for node in next_set - node_set:
                node.set_timestep(i)
            node_set = next_set

        if self.has_truth():
            self.find_truth_subgraphs()

    def find_truth_subgraphs(self) -> None:
        assert self.has_truth()
        subgraphs: tp.List[SubGraph] = self.subgraphs()

        truth: SubGraph = self.get_truth()
        if not truth.has_previous():
            truth.find_subgraphs()
        truth_subgraphs: tp.List[SubGraph] = truth.subgraphs()
        assert len(subgraphs) == len(truth_subgraphs)

        for i, subgraph in enumerate(subgraphs):
            truth_subgraph: SubGraph = truth_subgraphs[i]

            # check whether all elements already have their 'truth' reference populated
            if set(subgraph.get_elements()) <= set(self.get_elements()):
                subgraph._truth = truth_subgraph
            else:
                subgraph.assign_truth(truth_subgraph)

    # copy
    def copy_meta_to(self, graph: SubGraph) -> SubGraph:
        graph = super().copy_meta_to(graph)
        # note: _previous is not part of the metadata copied

        graph._truth = self._truth
        graph._pre = self._pre
        graph._date = self._date
        graph._atol = self._atol
        return graph


T = tp.TypeVar('T')


class Node(tp.Generic[T], FactorNode[T]):

    # reference to truth/unperturbed equivalent node
    _truth: tp.Optional[SubNode]
    _timestep: tp.Optional[int]

    # metrics
    _ate2: tp.Optional[float]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            timestep: tp.Optional[float] = None
    ):
        super().__init__(name=name, id_=id_, value=value)
        self._truth = None
        self._timestep = timestep
        self.clear_metrics()

    def clear_metrics(self) -> None:
        super().clear_metrics()
        self._ate2 = None

    # error
    def get_ate2(self) -> tp.Optional[float]:
        if self._ate2 is None:
            self.compute_ate2()
        return self._ate2

    def compute_ate2(self) -> tp.Optional[float]:
        self._ate2 = self._compute_ate2()
        return self._ate2

    def _compute_ate2(self) -> tp.Optional[float]:
        return None

    # truth
    def assign_truth(self, node: SubNode):
        assert not self.has_truth()
        assert node.get_id() == self.get_id()
        assert node.get_timestep() == self.get_timestep()
        self._truth = node

    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubNode:
        assert self.has_truth()
        return self._truth

    # timestep
    def set_timestep(self, timestep: int) -> None:
        assert not self.has_timestep()
        self._timestep = timestep

    def has_timestep(self) -> bool:
        return self._timestep is not None

    def get_timestep(self) -> tp.Optional[int]:
        return self._timestep

    # copy
    def copy_meta_to(self, node: SubNode) -> SubNode:
        node = super().copy_meta_to(node)
        node._truth = self._truth
        node._timestep = self._timestep
        return node

    def __copy__(self):
        new = super().__copy__()
        new._timestep = self._timestep
        new._truth = self._truth
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        new._timestep = self._timestep
        new._truth = self._truth
        return new


class Edge(tp.Generic[T], FactorEdge[T], ABC):

    # reference to truth/unperturbed equivalent edge
    _truth: tp.Optional[SubEdge]

    # metrics
    _rpet2: tp.Optional[float]
    _rper2: tp.Optional[float]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            nodes: tp.Optional[tp.List[SubEdge]] = None,
            measurement: tp.Optional[T] = None,
            info_matrix: tp.Optional['SubSquare'] = None
    ):
        super().__init__(name=name, nodes=nodes, measurement=measurement, info_matrix=info_matrix)
        self._truth = None
        self.clear_metrics()

    def clear_metrics(self) -> None:
        super().clear_metrics()
        self._rpet2 = None
        self._rper2 = None

    # DataContainer
    def has_measurement(self) -> bool:
        """ Returns whether a measurement has already been assigned to this edge. """
        return super().has_value()

    @abstractmethod
    def get_measurement(self) -> 'SubMeasurement':
        """ Returns the measurement encoded in this edge. """
        pass

    @abstractmethod
    def set_measurement(self, measurement: 'SubMeasurement') -> None:
        """ Sets the measurement encoded in this edge. """
        pass

    # error
    def get_rpe_translation2(self) -> tp.Optional[float]:
        if self._rpet2 is None:
            self.compute_rpe_translation2()
        return self._rpet2

    def get_rpe_rotation2(self) -> tp.Optional[float]:
        if self._rper2 is None:
            self.compute_rpe_rotation2()
        return self._rper2

    def compute_rpe_translation2(self) -> tp.Optional[float]:
        self._rpet2 = self._compute_rpe_translation2()
        return self._rpet2

    def compute_rpe_rotation2(self) -> tp.Optional[float]:
        self._rper2 = self._compute_rpe_rotation2()
        return self._rper2

    def _compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def _compute_rpe_rotation2(self) -> tp.Optional[float]:
        return None

    # truth
    def is_eligible_for_truth(self, edge: SubEdge):
        """ Returns whether the provided edge is connected to all this edge's nodes that have a 'truth' reference. """

        # truth_ids: tp.List[int] = [node.get_id() for node in self.get_nodes() if node.has_truth()]
        return edge.get_timestep() == self.get_timestep() and self.get_endpoint_ids() == edge.get_endpoint_ids()

    def assign_truth(self, edge: SubEdge):
        assert not self.has_truth()
        assert self.is_eligible_for_truth(edge)
        self._truth = edge

    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubEdge:
        assert self.has_truth()
        return self._truth

    # timestep
    def get_timestep(self) -> tp.Optional[int]:
        timesteps = [node.get_timestep() for node in self.get_nodes()]
        if None in timesteps:
            return None
        return max(timesteps)

    # copy
    def copy_meta_to(self, edge: SubEdge) -> SubEdge:
        edge = super().copy_meta_to(edge)
        edge._truth = self._truth
        return edge

    def __copy__(self):
        new = super().__copy__()
        new._truth = self._truth
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        new._truth = self._truth
        return new
