import pathlib
import typing as tp
from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.FactorGraph import FactorGraph, FactorNode, FactorEdge

if tp.TYPE_CHECKING:
    from src.framework.graph.protocols.Measurement import SubMeasurement
    from src.framework.math.matrix.square import SubSquare

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
    _error: tp.Optional[float]
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

        # properties
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

    def get_timestamp(self) -> tp.Optional[float]:
        return self.get_nodes()[-1].get_timestamp()

    # pre
    def has_pre(self) -> bool:
        return self._pre is not None

    def get_pre(self) -> SubGraph:
        assert self.has_pre()
        return self._pre

    def assign_pre(self, graph: SubGraph):
        assert self.is_equivalent(graph)
        self._pre = graph

    # error
    def compute_error(self) -> float:
        error: float = 0.
        for edge in self.get_edges():
            error += edge.compute_error()
        self._error = error
        return error

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

    def compute_rpe_rotation(self) -> float:
        """ Returns the rotation portion of the Relative Pose Error (RPE). """

        assert self.has_truth()
        rpe: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_rotation()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        self._rpe_rotation = rpe/count
        return self._rpe_rotation

    def get_error(self) -> float:
        if self._error is None:
            error: float = 0.
            for edge in self.get_edges():
                error += edge.get_error()
            self._error = error
        return self._error

    def get_ate(self) -> float:
        if self._ate is None:
            self.compute_ate()
        return self._ate

    def get_rpe_translation(self) -> float:
        if self._rpe_translation is None:
            self.compute_rpe_translation()
        return self._rpe_translation

    def get_rpe_rotation(self) -> float:
        if self._rpe_rotation is None:
            self.compute_rpe_rotation()
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

        # assigning timestamps to all nodes
        subgraphs: tp.List[SubGraph] = self.get_subgraphs()
        node_set: tp.Set[SubNode] = set()
        next_set: tp.Set[SubNode]
        for i, subgraph in enumerate(subgraphs):
            next_set = set(subgraph.get_nodes())

            node: SubNode
            for node in next_set - node_set:
                node.set_timestamp(i)
            node_set = next_set

        if self.has_truth():
            self.find_truth_subgraphs()

    def find_truth_subgraphs(self) -> None:
        assert self.has_truth()
        subgraphs: tp.List[SubGraph] = self.get_subgraphs()

        truth: SubGraph = self.get_truth()
        if not truth.has_previous():
            truth.find_subgraphs()
        truth_subgraphs: tp.List[SubGraph] = truth.get_subgraphs()
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
    _timestamp: tp.Optional[float]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None,
            timestamp: tp.Optional[float] = None
    ):
        super().__init__(name=name, id_=id_, value=value)
        self._timestamp = timestamp
        self._truth = None

    # error
    def compute_ate2(self) -> tp.Optional[float]:
        return None

    # truth
    def assign_truth(self, node: SubNode):
        assert not self.has_truth()
        assert node.get_id() == self.get_id()
        assert node.get_timestamp() == self.get_timestamp()
        self._truth = node

    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubNode:
        assert self.has_truth()
        return self._truth

    # timestamp
    def set_timestamp(self, timestamp: float) -> None:
        assert not self.has_timestamp()
        self._timestamp = timestamp

    def has_timestamp(self) -> bool:
        return self._timestamp is not None

    def get_timestamp(self) -> tp.Optional[float]:
        return self._timestamp

    # copy
    def copy_meta_to(self, node: SubNode) -> SubNode:
        node = super().copy_meta_to(node)
        node._truth = self._truth
        node._timestamp = self._timestamp
        return node

    def __copy__(self):
        new = super().__copy__()
        new._timestamp = self._timestamp
        new._truth = self._truth
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        new._timestamp = self._timestamp
        new._truth = self._truth
        return new


class Edge(tp.Generic[T], FactorEdge[T], ABC):

    # reference to truth/unperturbed equivalent edge
    _truth: tp.Optional[SubEdge]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            nodes: tp.Optional[tp.List[SubEdge]] = None,
            measurement: tp.Optional[T] = None,
            info_matrix: tp.Optional['SubSquare'] = None
    ):
        super().__init__(name=name, nodes=nodes, measurement=measurement, info_matrix=info_matrix)
        self._truth = None

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
    def compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def compute_rpe_rotation(self) -> tp.Optional[float]:
        return None

    # truth
    def is_eligible_for_truth(self, edge: SubEdge):
        """ Returns whether the provided edge is connected to all this edge's nodes that have a 'truth' reference. """

        # truth_ids: tp.List[int] = [node.get_id() for node in self.get_nodes() if node.has_truth()]
        return edge.get_timestamp() == self.get_timestamp() and self.get_endpoint_ids() == edge.get_endpoint_ids()

    def assign_truth(self, edge: SubEdge):
        assert not self.has_truth()
        assert self.is_eligible_for_truth(edge)
        self._truth = edge

    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubEdge:
        assert self.has_truth()
        return self._truth

    # timestamp
    def get_timestamp(self) -> tp.Optional[float]:
        timestamps = [node.get_timestamp() for node in self.get_nodes()]
        if None in timestamps:
            return None
        return max(timestamps)

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
