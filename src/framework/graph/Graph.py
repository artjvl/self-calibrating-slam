import copy
import pathlib
import typing as tp
from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np
from src.framework.graph.FactorGraph import FactorGraph, FactorNode, FactorEdge
from src.framework.math.matrix.vector import SubVector

SubGraph = tp.TypeVar('SubGraph', bound='Graph')
SubNode = tp.TypeVar('SubNode', bound='Node')
SubEdge = tp.TypeVar('SubEdge', bound='Edge')
SubElement = tp.Union[SubNode, SubEdge]


class Graph(FactorGraph):

    # reference graphs
    _true: tp.Optional[SubGraph]
    _pre: tp.Optional[SubGraph]

    # metadata
    _date: str
    _path: tp.Optional[pathlib.Path]

    # properties
    _error: tp.Optional[float]
    _ate: tp.Optional[float]
    _rpe_translation: tp.Optional[float]
    _rpe_rotation: tp.Optional[float]

    def __init__(self):
        super().__init__()

        # reference graphs
        self._true = None
        self._pre = None

        # metadata
        self._date = datetime.now().strftime('%Y%m%d-%H%M%S')
        self._path = None

        # properties
        self._error = None
        self._ate = None
        self._rpe_translation = None
        self._rpe_rotation = None

    # pre
    def has_pre(self) -> bool:
        return self._pre is not None

    def get_pre(self) -> SubGraph:
        assert self.has_pre()
        return self._pre

    def assign_pre(self, graph: SubGraph):
        assert len(self.get_nodes()) == len(graph.get_nodes())
        # assert len(self.get_edges()) == len(graph.get_edges())
        self._pre = graph

    # true
    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubGraph:
        assert self.has_true()
        return self._true

    def is_perturbed(self) -> bool:
        return not np.isclose(self.get_error(), 0.)

    def has_metrics(self) -> bool:
        return self.is_perturbed() and self.has_true()

    def assign_true(self, graph: SubGraph):
        assert self.is_perturbed()
        assert not graph.is_perturbed()

        nodes: tp.List[SubNode] = self.get_nodes()
        true_nodes: tp.List[SubNode] = graph.get_nodes()
        assert len(nodes) == len(true_nodes)
        for i, node in enumerate(nodes):
            true_node = true_nodes[i]
            node.assign_true(true_node)

        edges: tp.List[SubEdge] = self.get_edges()
        true_edges: tp.List[SubEdge] = graph.get_edges()
        assert len(edges) == len(true_edges)
        for i, edge in enumerate(edges):
            true_edge = true_edges[i]
            edge.assign_true(true_edge)

        self._true = graph

    # error
    def compute_error(self) -> float:
        error: float = 0.
        for edge in self.get_edges():
            error += edge.compute_error()
        self._error = error
        return error

    def compute_ate(self) -> float:
        """ Returns the Absolute Trajectory Error (APE). """

        assert self.has_metrics()
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

        assert self.has_metrics()
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

        assert self.has_metrics()
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

    # errors
    def get_error(self) -> float:
        if self._error is None:
            self.compute_error()
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

    # properties
    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def get_path(self) -> pathlib.Path:
        return self._path

    def get_pathname(self) -> str:
        return self._path.name

    def __copy__(self):
        new = super().__copy__()
        new._true = copy.copy(self._true)
        new._pre = copy.copy(self._pre)
        new._date = copy.copy(self._date)
        new._ate = self._ate
        new._rpe_translation = self._rpe_translation
        new._rpe_rotation = self._rpe_rotation
        return new


T = tp.TypeVar('T')


class Node(tp.Generic[T], FactorNode[T]):

    # reference to true/unperturbed equivalent node
    _true: tp.Optional[SubNode]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._true = None

    # true
    def assign_true(self, node: SubNode):
        assert self.get_id() == node.get_id()
        self._true = node

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubNode:
        assert self.has_true()
        return self._true

    # error
    def compute_ate2(self) -> tp.Optional[float]:
        return None


class Edge(tp.Generic[T], FactorEdge[T], ABC):

    # reference to true/unperturbed equivalent edge
    _true: tp.Optional[SubEdge]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._true = None

    # error
    @abstractmethod
    def compute_error_vector(self) -> SubVector:
        pass

    def error_vector(self) -> SubVector:
        return self.compute_error_vector()

    def compute_error(self) -> float:
        error_vector: SubVector = self.error_vector()
        return self.mahalanobis_distance(error_vector, self.get_info_matrix())

    def compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def compute_rpe_rotation(self) -> tp.Optional[float]:
        return None

    # true
    def assign_true(self, edge: SubEdge):
        nodes = self.get_nodes()
        true_nodes = edge.get_nodes()
        assert len(nodes) == len(true_nodes)

        node: SubNode
        for i, node in enumerate(nodes):
            true_node = true_nodes[i]
            assert node.get_id() == true_node.get_id()
            assert node.has_true()
        self._true = edge

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubEdge:
        assert self.has_true()
        return self._true
