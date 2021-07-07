import copy
import pathlib
import typing as tp
from abc import ABC, abstractmethod
from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np
from src.framework.graph.FactorGraph import FactorGraph, FactorNode, FactorEdge
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector.Vector import Vector

SubGraph = tp.TypeVar('SubGraph', bound='Graph')
SubNode = tp.TypeVar('SubNode', bound='Node')
SubEdge = tp.TypeVar('SubEdge', bound='Edge')
SubElement = tp.Union[SubNode, SubEdge]


class Graph(FactorGraph):

    _true: tp.Optional[SubGraph]
    _pre: tp.Optional[SubGraph]

    def __init__(self):
        super().__init__()
        self._true = None
        self._pre = None

        self._date: str = datetime.now().strftime('%Y%m%d-%H%M%S')
        self._path: tp.Optional[pathlib.Path] = None
        self._suffix: tp.Optional[str] = None

        self._error: tp.Optional[float] = None
        self._ate: tp.Optional[float] = None
        self._rpe_translation: tp.Optional[float] = None
        self._rpe_rotation: tp.Optional[float] = None

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

    def error_curve(self, steps: int = 50) -> tp.Tuple[tp.List[float], tp.List[float]]:
        assert self.has_true()
        assert self.has_pre()

        pre_vector: SubVector = self.get_pre().to_vector()
        opt_vector: SubVector = self.to_vector()
        unit: SubVector = Vector(pre_vector.array() - opt_vector.array())

        graph: SubGraph = copy.deepcopy(self)
        line = list(np.linspace(-2, 2, steps + 1))
        error = []
        for x in line:
            vector = Vector(opt_vector.array() + unit.array() * x)
            graph.from_vector(vector)
            error.append(graph.compute_error())
        plt.plot(line, error)
        plt.show()
        return line, error

    # true
    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubGraph:
        assert self.has_true()
        return self._true

    def is_perturbed(self) -> bool:
        return not np.isclose(self.compute_error(), 0.)

    def is_metric(self) -> bool:
        return self.is_perturbed() and self.has_true()

    def assign_true(self, graph: SubGraph):
        # assert self.is_perturbed()
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
        return error

    def compute_ate(self) -> float:
        """ Returns the Absolute Trajectory Error (APE). """

        assert self.is_metric()
        ate: float = 0
        count: int = 0
        node: SubNode
        for node in self.get_nodes():
            node_ate = node.compute_ate2()
            if node_ate is not None:
                ate += node_ate
                count += 1
        return np.sqrt(ate/count)

    def compute_rpe_translation(self) -> float:
        """ Returns the translation portion of the Relative Pose Error (RPE). """

        assert self.is_metric()
        rpe2: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_translation2()
            if edge_rpe2 is not None:
                rpe2 += edge_rpe2
                count += 1
        return np.sqrt(rpe2/count)

    def compute_rpe_rotation(self) -> float:
        """ Returns the rotation portion of the Relative Pose Error (RPE). """

        assert self.is_metric()
        rpe: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_rotation()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        return rpe/count

    # subgraphs
    def get_subgraphs(self) -> tp.List[SubGraph]:
        graphs: tp.List[SubGraph] = super().get_subgraphs()
        if self.has_true():
            true_graphs: tp.List[SubGraph] = self.get_true().get_subgraphs()
            for i, graph in graphs:
                true_graph: SubGraph = true_graphs[i]
                graph.assign_true(true_graph)
        return graphs

    # errors
    def get_error(self) -> float:
        if self._error is None:
            self._error = self.compute_error()
        return self._error

    def get_ate(self) -> float:
        if self._ate is None:
            self._ate = self.compute_ate()
        return self._ate

    def get_rpe_translation(self) -> float:
        if self._rpe_translation is None:
            self._rpe_translation = self.compute_rpe_translation()
        return self._rpe_translation

    def get_rpe_rotation(self) -> float:
        if self._rpe_rotation is None:
            self._rpe_rotation = self.compute_rpe_rotation()
        return self._rpe_rotation

    # properties
    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def get_path(self) -> pathlib.Path:
        return self._path

    def get_pathname(self) -> str:
        return self._path.name


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
        for i, node in enumerate(nodes):
            true_node = true_nodes[i]
            assert node.get_id() == true_node.get_id()
        self._true = edge

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubEdge:
        assert self.has_true()
        return self._true
