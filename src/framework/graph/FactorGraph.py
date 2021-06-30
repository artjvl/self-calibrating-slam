import copy
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.BaseGraph import BaseGraph, BaseNode, BaseEdge
from src.framework.graph.BlockMatrix import SparseBlockMatrix, BlockMatrix, SubSparseBlockMatrix, SubBlockMatrix
from src.framework.graph.data import SubData, DataFactory
from src.framework.graph.data import SubDataSymmetric
from src.framework.math.matrix.Matrix import SubMatrix, List2D, Matrix
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector import VectorFactory

SubFactorGraph = tp.TypeVar('SubFactorGraph', bound='FactorGraph')
SubFactorNode = tp.TypeVar('SubFactorNode', bound='FactorNode')
SubFactorEdge = tp.TypeVar('SubFactorEdge', bound='FactorEdge')
SubFactorElement = tp.Union[SubFactorNode, SubFactorEdge]


class FactorGraph(BaseGraph):

    _hessian: SubSparseBlockMatrix
    _covariance: tp.Optional[SubBlockMatrix]

    def __init__(self):
        super().__init__()
        self.init_gradient()
        self._covariance = None

    def add_node(self, node: SubFactorNode) -> None:
        super().add_node(node)
        self.init_gradient()

    # linearise
    def init_gradient(self) -> None:
        node_dims: tp.List[int] = [node.get_dim() for node in self.get_nodes()]
        self._hessian = SparseBlockMatrix(node_dims)

    def get_hessian(self) -> SubSparseBlockMatrix:
        if not self._hessian:
            print(f'Linearising {self.to_unique()}..')
            self.linearise()
        return self._hessian

    def linearise(self) -> None:
        edges: tp.List[FactorEdge] = self.get_edges()
        for edge in edges:
            nodes: tp.List[FactorNode] = edge.get_nodes()
            for node_i in nodes:
                for node_j in nodes:
                    i: int = self.get_node_index(node_i)
                    j: int = self.get_node_index(node_j)
                    # print(f'{i}-{j}')
                    self._hessian[i, j] = self._hessian[i, j] + \
                        edge.get_hessian()[edge.get_node_index(node_i), edge.get_node_index(node_j)]

    def get_covariance(self) -> SubBlockMatrix:
        if self._covariance is None:
            hessian: SubSparseBlockMatrix = self.get_hessian()
            matrix: np.ndarray = hessian.inverse()
            self._covariance = BlockMatrix.from_array(matrix, hessian.get_row_sizes())
        return self._covariance

    def get_marginals(self) -> tp.List[SubMatrix]:
        covariance: SubBlockMatrix = self.get_covariance()
        marginals: tp.List[SubMatrix] = []
        for i, _ in enumerate(covariance.get_row_sizes()):
            marginals.append(covariance[i, i])
        return marginals


T = tp.TypeVar('T')


class FactorNode(tp.Generic[T], BaseNode):

    # value variables
    _type: tp.Type[T]
    _value: SubData

    # properties
    _is_fixed: bool

    def __init__(
            self,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None
    ):
        if id_ is None:
            id_ = 0
        super().__init__(id_)
        self._value = DataFactory.from_type(self.get_type())(value)
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

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._value.read_rest(words)
        assert not words, f"Words '{words} are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._value.write()
        return words


class FactorEdge(tp.Generic[T], BaseEdge):

    # measurement variables
    _type: tp.Type[T]
    _measurement: SubData
    _info_matrix: SubDataSymmetric

    # gradient
    _jacobian: BlockMatrix
    _hessian: BlockMatrix

    def __init__(
            self,
            measurement: tp.Optional[T] = None,
            info_matrix: tp.Optional[SubSquare] = None,
            *nodes: tp.Optional[SubFactorNode]
    ):
        super().__init__(*[node for node in nodes if node is not None])
        self._measurement = DataFactory.from_type(self.get_type())(measurement)
        if info_matrix is None:
            info_matrix = SquareFactory.from_dim(self.get_dim()).identity()
        self._info_matrix = DataFactory.from_value(info_matrix)
        self.init_gradient()

    def add_node(self, node: SubFactorNode) -> None:
        super().add_node(node)
        self.init_gradient()

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

    def get_cov_matrix(self) -> SubSquare:
        """ Returns the covariance matrix of this edge. """
        return self._info_matrix.get_value().inverse()

    def set_info_matrix(self, info_matrix: SubSquare) -> None:
        """ Sets the information matrix of this edge. """
        self._info_matrix.set_value(info_matrix)

    def set_cov_matrix(self, cov_matrix: SubSquare) -> None:
        """ Sets the information matrix of this edge by providing the covariance matrix. """
        self._info_matrix.set_value(cov_matrix.inverse())


    # helper methods
    @staticmethod
    def mahalanobis_distance(
            vector: SubVector,
            information: SubSquare
    ) -> float:
        assert vector.get_dim() == information.get_dim(), f'{vector} and {information} are not of appropriate dimensions.'
        return float(vector.array().transpose() @ information.array() @ vector.array())

    # linearisation
    def init_gradient(self) -> None:
        node_dims: tp.List[int] = [node.get_dim() for node in self.get_nodes()]
        self._jacobian = BlockMatrix([self.get_dim()], node_dims)
        self._hessian = BlockMatrix(node_dims, node_dims)

    def get_jacobian(self) -> SubBlockMatrix:
        if not self._jacobian:
            self.linearise()
        return self._jacobian

    def get_hessian(self) -> SubBlockMatrix:
        if not self._hessian:
            self.linearise()
        return self._hessian

    def linearise(self) -> None:
        id_: int
        node: SubFactorNode
        nodes: tp.List[SubFactorNode] = self.get_nodes()
        for node in nodes:
            self._jacobian[0, self.get_node_index(node)] = self.central_difference(node)

        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                jacobian_i: SubMatrix = self._jacobian[0, i]
                jacobian_j: SubMatrix = self._jacobian[0, j]
                block: SubMatrix = Matrix(jacobian_i.array().transpose() @ self.get_info_matrix().array() @ jacobian_j.array())
                self._hessian[i, j] = block

    def central_difference(self, node: tp.Union[int, SubFactorNode]) -> SubMatrix:
        if isinstance(node, int):
            node = self.get_node(node)
        id_: int = node.get_id()

        delta: float = 1e-9
        jacobian: List2D = []
        for i in range(node.get_dim()):
            edge_copy: SubFactorEdge = copy.deepcopy(self)
            node_copy: SubFactorNode = edge_copy.get_node(id_)

            mean: SubData = copy.deepcopy(node_copy._value)
            unit_vector: SubVector = VectorFactory.from_dim(self.get_dim()).zeros()

            unit_vector[i] = delta
            plus: T = mean.oplus(unit_vector)
            node_copy.set_value(plus)
            plus_error: SubVector = edge_copy.error_vector()

            unit_vector[i] = - delta
            minus: T = mean.oplus(unit_vector)
            node_copy.set_value(minus)
            minus_error: SubVector = edge_copy.error_vector()
            error = plus_error.array() - minus_error.array()

            column: SubVector = VectorFactory.from_dim(self.get_dim())(
                error / (2 * delta)
            )
            jacobian.append(column.to_list())
        return Matrix(np.array(jacobian).transpose())

    @abstractmethod
    def get_cardinality(self) -> int:
        pass

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._measurement.read_rest(words)
        words = self._info_matrix.read_rest(words)
        assert not words, f"Words '{words} are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._measurement.write() + self._info_matrix.write()
        return words
