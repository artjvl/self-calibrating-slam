import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.BaseGraph import BaseGraph, BaseNode, BaseEdge
from src.framework.graph.protocols.ReadWrite import ReadWrite
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector

SubFactorGraph = tp.TypeVar('SubFactorGraph', bound='FactorGraph')
SubFactorNode = tp.TypeVar('SubFactorNode', bound='FactorNode')
SubFactorEdge = tp.TypeVar('SubFactorEdge', bound='FactorEdge')
SubElement = tp.Union[SubFactorNode, SubFactorEdge]


class FactorGraph(BaseGraph):

    def __init__(self):
        super().__init__()
        self._true: tp.Optional[SubFactorGraph] = None

    def is_perturbed(self) -> bool:
        return not np.isclose(self.compute_error(), 0.)

    # true
    def assign_true(self, graph: SubFactorGraph):
        # assert self.is_perturbed()
        assert not graph.is_perturbed()

        nodes: tp.List[SubFactorNode] = self.get_nodes()
        true_nodes: tp.List[SubFactorNode] = graph.get_nodes()
        assert len(nodes) == len(true_nodes)
        for i, node in enumerate(nodes):
            true_node = true_nodes[i]
            node.assign_true(true_node)

        edges: tp.List[SubFactorEdge] = self.get_edges()
        true_edges: tp.List[SubFactorEdge] = graph.get_edges()
        assert len(edges) == len(true_edges)
        for i, edge in enumerate(edges):
            true_edge = true_edges[i]
            edge.assign_true(true_edge)

        self._true = graph

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubFactorGraph:
        assert self.has_true()
        return self._true

    # error
    def compute_error(self) -> float:
        error: float = 0
        for edge in self.get_edges():
            error += edge.compute_error()
        return error

    def compute_ate(self) -> float:
        """ Returns the Absolute Trajectory Error (APE). """

        assert self.is_perturbed()
        assert self.has_true()
        ate: float = 0
        node: SubFactorNode
        for node in self.get_nodes():
            ate += node.compute_ate2()
        return np.sqrt(ate)

    def compute_rpe_translation(self) -> float:
        """ Returns the translation portion of the Relative Pose Error (RPE). """

        assert self.is_perturbed()
        assert self.has_true()
        rpe2: float = 0
        count: int = 0
        edge: SubFactorEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_translation2()
            if edge_rpe2 is not None:
                rpe2 += edge_rpe2
                count += 1
        return np.sqrt(rpe2/count)

    def compute_rpe_rotation(self) -> float:
        """ Returns the rotation portion of the Relative Pose Error (RPE). """

        assert self.is_perturbed()
        assert self.has_true()
        rpe: float = 0
        count: int = 0
        edge: SubFactorEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_rotation()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        return rpe/count


T = tp.TypeVar('T')


class FactorNode(tp.Generic[T], BaseNode, ReadWrite):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__(id_)
        self._true: tp.Optional[SubFactorNode] = None
        self._is_fixed = False

    def fix(self, is_fixed: bool = True) -> None:
        self._is_fixed = is_fixed

    def is_fixed(self) -> bool:
        return self._is_fixed

    # true
    def assign_true(self, node: SubFactorNode):
        assert self.get_id() == node.get_id()
        self._true = node

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubFactorNode:
        assert self.has_true()
        return self._true

    # error
    def compute_ate2(self) -> tp.Optional[float]:
        return None

    # value
    @abstractmethod
    def get_value(self) -> T:
        pass


class FactorEdge(tp.Generic[T], BaseEdge, ReadWrite):

    def __init__(
            self,
            *nodes: SubFactorNode
    ):
        super().__init__(*nodes)
        self._true: tp.Optional[SubFactorEdge] = None

    @abstractmethod
    def get_cardinality(self) -> int:
        pass

    # measurement
    @abstractmethod
    def get_measurement(self) -> T:
        """ Returns the (externally assigned) measurement encoded in the edge. """
        pass

    # estimate
    @abstractmethod
    def get_estimate(self) -> T:
        """ Returns an estimate of the measurement. """
        pass

    # information
    @abstractmethod
    def get_information(self) -> SubSquare:
        pass

    # error
    @abstractmethod
    def compute_error_vector(self) -> SubVector:
        pass

    def compute_error(self) -> float:
        error_vector: SubVector = self.compute_error_vector()
        return self.mahalanobis_distance(error_vector, self.get_information())

    def compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def compute_rpe_rotation(self) -> tp.Optional[float]:
        return None

    # true
    def assign_true(self, edge: SubFactorEdge):
        nodes = self.get_nodes()
        true_nodes = edge.get_nodes()
        assert len(nodes) == len(true_nodes)
        for i, node in enumerate(nodes):
            true_node = true_nodes[i]
            assert node.get_id() == true_node.get_id()
        self._true = edge

    def has_true(self) -> bool:
        return self._true is not None

    def get_true(self) -> SubFactorEdge:
        assert self.has_true()
        return self._true

    # helper methods
    @staticmethod
    def mahalanobis_distance(
            vector: SubVector,
            information: SubSquare
    ) -> float:
        assert vector.get_dimension() == information.get_dimension(), f'{vector} and {information} are not of appropriate dimensions.'
        return float(vector.array().transpose() @ information.inverse().array() @ vector.array())
