import copy
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.BaseGraph import BaseGraph, BaseNode, BaseEdge
from src.framework.graph.data import SubData, DataFactory
from src.framework.graph.data import SubDataSymmetric
from src.framework.graph.protocols.ReadWrite import ReadWrite
from src.framework.math.matrix.Matrix import SubMatrix, List2D, Matrix
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector import VectorFactory

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

    def is_metric(self) -> bool:
        return self.is_perturbed() and self.has_true()

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

        assert self.is_metric()
        ate: float = 0
        count: int = 0
        node: SubFactorNode
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
        edge: SubFactorEdge
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
        edge: SubFactorEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.compute_rpe_rotation()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        return rpe/count

    def get_subgraphs(self) -> tp.List[SubFactorGraph]:
        graphs: tp.List[SubFactorGraph] = super().get_subgraphs()
        if self.has_true():
            true_graphs: tp.List[SubFactorGraph] = self.get_true().get_subgraphs()
            for i, graph in graphs:
                true_graph: SubFactorGraph = true_graphs[i]
                graph.assign_true(true_graph)
        return graphs


T = tp.TypeVar('T')


class FactorNode(tp.Generic[T], BaseNode, ReadWrite):

    # value variables
    _type: tp.Type[T]
    _value: SubData

    # properties
    _is_fixed: bool

    # reference to true/unperturbed equivalent node
    _true: tp.Optional[SubFactorNode]

    def __init__(
            self,
            id_: int = 0,
            value: tp.Optional[T] = None
    ):
        super().__init__(id_)
        self._value = DataFactory.from_type(self.get_type())(value)

        self._true = None
        self._is_fixed = False

    # value
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the value-type of this node. """
        return cls._type

    @classmethod
    def get_dim(cls) -> int:
        """ Returns the dimensions (minimum number of constraints) for the value-type of this node. """
        return DataFactory.from_type(cls.get_type()).get_dim()

    def has_value(self) -> bool:
        """ Returns whether a value has already been assigned to this node. """
        return self._value.has_value()

    def get_value(self) -> T:
        """ Returns the value encoded in this node. """
        assert self.has_value()
        return self._value.get_value()

    def set_value(self, value: T) -> None:
        """ Sets the value of this node. """
        self._value.set_value(value)

    # fix
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

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._value.read_rest(words)
        assert not words, f"Words '{words} are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._value.write()
        return words

    @classmethod
    def get_length(cls) -> int:
        return cls.get_dim()


class FactorEdge(tp.Generic[T], BaseEdge, ReadWrite):

    # measurement variables
    _type: tp.Type[T]
    _measurement: SubData
    _info_matrix: SubDataSymmetric

    # reference to true/unperturbed equivalent edge
    _true: tp.Optional[SubFactorEdge]

    # gradient
    _jacobians: tp.Dict[int, SubMatrix]

    def __init__(
            self,
            *nodes: SubFactorNode
    ):
        super().__init__(*nodes)
        self._measurement = DataFactory.from_type(self.get_type())()
        self._info_matrix = DataFactory.from_value(
            SquareFactory.from_dim(self.get_dim()).identity()
        )

        self._true = None
        self._jacobians = {}

    # measurement
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the measurement-type of this edge. """
        return cls._type

    @classmethod
    def get_dim(cls) -> int:
        """ Returns the dimensions (minimum number of constraints) for the measurement-type of this edge. """
        return DataFactory.from_type(cls.get_type()).get_dim()

    def has_measurement(self) -> bool:
        """ Returns whether a measurement has already been assigned to this edge. """
        return self._measurement.has_value()

    def get_measurement(self) -> T:
        """ Returns the measurement encoded in this edge. """
        assert self.has_measurement()
        return self._measurement.get_value()

    def set_measurement(self, measurement: T) -> None:
        """ Sets the measurement of this edge. """
        self._measurement.set_value(measurement)

    # estimate
    @abstractmethod
    def get_estimate(self) -> T:
        """ Returns an estimate of the measurement. """
        pass

    # information
    def get_info_matrix(self) -> SubSquare:
        """ Returns the information matrix of this edge. """
        return self._info_matrix.get_value()

    def set_info_matrix(self, info_matrix: SubSquare) -> None:
        """ Sets the information matrix of this edge. """
        self._info_matrix.set_value(info_matrix)

    # error
    @abstractmethod
    def compute_error_vector(self) -> SubVector:
        pass

    def compute_error(self) -> float:
        error_vector: SubVector = self.compute_error_vector()
        return self.mahalanobis_distance(error_vector, self.get_info_matrix())

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
        return float(vector.array().transpose() @ information.array() @ vector.array())

    # linearisation
    def linearise(self) -> tp.Dict[int, SubMatrix]:
        if not self._jacobians:
            id_: int
            node: SubFactorNode
            for id_, node in self._nodes.items():
                self._jacobians[id_] = self.central_difference(node)
        return self._jacobians

    def central_difference(self, node: SubFactorNode) -> SubMatrix:
        id_: int = node.get_id()
        delta: float = 1e-9

        jacobian: List2D = []
        for i in range(node.get_dim()):
            edge: SubFactorEdge = copy.deepcopy(self)
            node: SubFactorNode = edge.get_node(id_)

            mean: SubData = node._measurement
            unit_vector: SubVector = VectorFactory.from_dim(self.get_dim())

            unit_vector[i] = delta
            plus: T = mean.oplus(unit_vector)
            node.set_value(plus)
            plus_error: SubVector = edge.compute_error_vector()

            unit_vector[i] = - delta
            minus: T = mean.oplus(unit_vector)
            node.set_value(minus)
            minus_error: SubVector = edge.compute_error_vector()

            column: SubVector = VectorFactory.from_dim(self.get_dim())(
                (plus_error.array() + minus_error.array()) / (2 * delta)
            )
            jacobian.append(column.to_list())
        return Matrix(np.array(jacobian).transpose())

    @abstractmethod
    def get_cardinality(self) -> int:
        pass
