import copy
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.BaseGraph import BaseGraph, BaseNode, BaseEdge
from src.framework.graph.data import DataFactory
from src.framework.math.matrix.BlockMatrix import SparseBlockMatrix, BlockMatrix
from src.framework.math.matrix.Matrix import List2D, Matrix
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.vector import VectorFactory
from src.framework.math.matrix.vector.Vector import Vector

if tp.TYPE_CHECKING:
    from src.framework.graph.data import SubData
    from src.framework.graph.data import SubDataSymmetric
    from src.framework.math.matrix.BlockMatrix import SubSparseBlockMatrix, SubBlockMatrix
    from src.framework.math.matrix.Matrix import SubMatrix
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector.Vector import SubVector, SubSizeVector


SubFactorGraph = tp.TypeVar('SubFactorGraph', bound='FactorGraph')
SubFactorNode = tp.TypeVar('SubFactorNode', bound='FactorNode')
SubFactorEdge = tp.TypeVar('SubFactorEdge', bound='FactorEdge')
SubFactorElement = tp.Union[SubFactorNode, SubFactorEdge]


class FactorGraph(BaseGraph):

    _hessian: tp.Optional['SubSparseBlockMatrix']
    _covariance: tp.Optional['SubSparseBlockMatrix']

    def __init__(self):
        super().__init__()
        self._hessian = None
        self._covariance = None

    def to_vector(self) -> 'SubVector':
        list_: tp.List[float] = []
        node: SubFactorNode
        for node in self.get_nodes():
            list_ += node.to_vector().to_list()
        return Vector(list_)

    def from_vector(self, vector: 'SubVector') -> None:
        graph_dim: int = sum([node.get_dim() for node in self.get_nodes()])
        vector_dim = vector.get_length()
        assert vector_dim <= graph_dim
        list_: tp.List[float] = vector.to_list()

        index: int = 0
        node_iter: iter = iter(self.get_nodes())
        node: SubFactorNode

        while index < vector_dim:
            node = next(node_iter, None)
            assert node is not None

            dim = node.get_dim()
            segment: tp.List[float] = list_[index: index + dim]
            assert len(segment) == dim
            node.from_vector(VectorFactory.from_list(segment))
            index += dim
        assert index == len(list_)

    # linearise
    def get_hessian(self) -> 'SubSparseBlockMatrix':
        if self._hessian is None:
            print(f'Linearising {self.to_unique()}..')
            self.linearise()
        return self._hessian

    def linearise(self) -> None:
        self._hessian = SparseBlockMatrix([node.get_dim() for node in self.get_active_nodes()])
        edges: tp.List[FactorEdge] = self.get_edges()
        for edge in edges:
            nodes: tp.List[FactorNode] = edge.get_active_nodes()
            for node_i in nodes:
                for node_j in nodes:
                    i: int = self.get_active_node_index(node_i.get_id())
                    j: int = self.get_active_node_index(node_j.get_id())
                    # print(f'{i}-{j}')
                    self._hessian[i, j] = self._hessian[i, j] + \
                        edge.get_hessian()[edge.get_active_node_index(node_i.get_id()), edge.get_active_node_index(node_j.get_id())]

    def get_covariance(self) -> 'SubSparseBlockMatrix':
        if self._covariance is None:
            hessian: 'SubSparseBlockMatrix' = self.get_hessian().diagonal()
            # chol = np.linalg.cholesky(hessian.array())
            matrix: np.ndarray = hessian.inverse()
            self._covariance = SparseBlockMatrix.from_array(matrix, hessian.get_row_sizes())
        return self._covariance

    def get_marginals(self) -> tp.List['SubMatrix']:
        covariance: 'SubSparseBlockMatrix' = self.get_covariance()
        marginals: tp.List['SubMatrix'] = []
        for i, _ in enumerate(covariance.get_row_sizes()):
            marginals.append(covariance[i, i])
        return marginals

    # copy
    def __copy__(self):
        new = super().__copy__()

        # # FactorGraph
        # new._hessian = self._hessian
        # new._covariance = self._covariance
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        # # FactorGraph
        # new._hessian = copy.deepcopy(self._hessian, memo)
        # new._covariance = copy.deepcopy(self._covariance, memo)
        return new


T = tp.TypeVar('T')


class DataContainer(tp.Generic[T]):

    _type: tp.Type[T]
    _data: 'SubData'

    def __init__(
            self,
            value: tp.Optional[T] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._data = DataFactory.from_type(self.get_type())(value)

    # type
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the value-type of this container. """
        return cls._type

    @classmethod
    def get_dim(cls) -> int:
        """ Returns the dimensions (minimum number of constraints) for the value-type of this container. """
        return DataFactory.from_type(cls.get_type()).get_dim()

    def get_data(self) -> 'SubData':
        return self._data

    # value
    def has_value(self) -> bool:
        """ Returns whether a value has already been assigned to this container. """
        return self._data.has_value()

    def get_value(self) -> T:
        """ Returns the value encoded in this container. """
        assert self.has_value()
        return self._data.get_value()

    def set_value(self, value: T) -> None:
        """ Sets the value of this container. """
        self._data.set_value(value)

    # vector
    def to_vector(self) -> 'SubSizeVector':
        """ Returns the vector that defines the value of this container. """
        return self._data.to_vector()

    def from_vector(self, vector: 'SubSizeVector') -> None:
        """ Sets the value of this container according to the provided vector. """
        self._data.from_vector(vector)

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        return self._data.read_rest(words)

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._data.write()
        return words


class FactorNode(BaseNode, tp.Generic[T], DataContainer[T]):

    # properties
    _is_fixed: bool

    def __init__(
            self,
            name: tp.Optional[str] = None,
            id_: tp.Optional[int] = None,
            value: tp.Optional[T] = None
    ):
        super().__init__(name=name, id_=id_, value=value)
        self._is_fixed = False

    # fix
    def fix(self, is_fixed: bool = True) -> None:
        self._is_fixed = is_fixed

    def is_fixed(self) -> bool:
        return self._is_fixed

    # copy
    def copy_meta_to(self, node: SubFactorNode) -> SubFactorNode:
        node = super().copy_meta_to(node)
        node._is_fixed = self._is_fixed
        return node

    # copy
    def __copy__(self):
        new = super().__copy__()

        # FactorNode
        new._is_fixed = self._is_fixed
        # DataContainer
        new.set_value(self.get_value())
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}

        # class
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        # FactorNode
        new._is_fixed = self._is_fixed
        # DataContainer
        new.set_value(copy.deepcopy(self.get_value()))
        return new


class FactorEdge(BaseEdge, tp.Generic[T], DataContainer[T]):

    _info_matrix: 'SubDataSymmetric'
    _error_vector: tp.Optional['SubSizeVector']

    # gradient
    _jacobian: tp.Optional['SubBlockMatrix']
    _hessian: tp.Optional['SubBlockMatrix']

    def __init__(
            self,
            name: tp.Optional[str] = None,
            nodes: tp.Optional[tp.List[SubFactorNode]] = None,
            measurement: tp.Optional[T] = None,
            info_matrix: tp.Optional['SubSquare'] = None
    ):
        super().__init__(name=name, nodes=nodes, value=measurement)
        if info_matrix is None:
            info_matrix = SquareFactory.from_dim(self.get_dim()).identity()
        self._info_matrix = DataFactory.from_value(info_matrix)
        self._error_vector = None

        self._jacobian = None
        self._hessian = None

    # estimate
    @abstractmethod
    def get_estimate(self) -> T:
        """ Returns the estimate of the measurement. """
        pass

    @abstractmethod
    def compute_error_vector(self) -> 'SubSizeVector':
        pass

    def get_error_vector(self) -> 'SubSizeVector':
        if self._error_vector is None:
            self._error_vector = self.compute_error_vector()
        return self._error_vector

    def compute_error(self) -> float:
        error_vector: 'SubSizeVector' = self.compute_error_vector()
        return self.mahalanobis_distance(error_vector, self.get_info_matrix())

    def get_error(self) -> float:
        error_vector: 'SubSizeVector' = self.get_error_vector()
        return self.mahalanobis_distance(error_vector, self.get_info_matrix())

    # information
    def get_info_matrix(self) -> 'SubSquare':
        """ Returns the information matrix of this edge. """
        return self._info_matrix.get_value()

    def set_info_matrix(self, info_matrix: 'SubSquare') -> None:
        """ Sets the information matrix of this edge. """
        self._info_matrix.set_value(info_matrix)

    def get_cov_matrix(self) -> 'SubSquare':
        """ Returns the covariance matrix of this edge. """
        return self._info_matrix.get_value().inverse()

    def set_cov_matrix(self, cov_matrix: 'SubSquare') -> None:
        """ Sets the information matrix of this edge by providing the covariance matrix. """
        self._info_matrix.set_value(cov_matrix.inverse())

    # helper methods
    @staticmethod
    def mahalanobis_distance(
            vector: 'SubSizeVector',
            information: 'SubSquare'
    ) -> float:
        assert vector.get_dim() == information.get_dim(), f'{vector} and {information} are not of appropriate dimensions.'
        return float(vector.array().transpose() @ information.array() @ vector.array())

    # linearisation
    def get_jacobian(self) -> 'SubBlockMatrix':
        if not self._jacobian:
            self.linearise()
        return self._jacobian

    def get_hessian(self) -> 'SubBlockMatrix':
        if not self._hessian:
            self.linearise()
        return self._hessian

    def linearise(self) -> None:
        nodes: tp.List[SubFactorNode] = self.get_active_nodes()
        node_dims: tp.List[int] = [node.get_dim() for node in nodes]
        self._jacobian = BlockMatrix([self.get_dim()], node_dims)

        node: SubFactorNode
        for node in nodes:
            self._jacobian[0, self.get_active_node_index(node.get_id())] = self.central_difference(node)

        self._hessian = BlockMatrix(node_dims)
        node_i: SubFactorNode
        node_j: SubFactorNode
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                jacobian_i: 'SubMatrix' = self._jacobian[0, i]
                jacobian_j: 'SubMatrix' = self._jacobian[0, j]
                block: 'SubMatrix' = Matrix(jacobian_i.array().transpose() @ self.get_info_matrix().array() @ jacobian_j.array())
                self._hessian[i, j] = block

    def central_difference(self, node: tp.Union[int, SubFactorNode]) -> 'SubMatrix':
        if isinstance(node, int):
            node = self.get_node(node)
        id_: int = node.get_id()

        delta: float = 1e-9
        jacobian: List2D = []
        for i in range(node.get_dim()):
            edge_copy: SubFactorEdge = copy.deepcopy(self)
            node_copy: SubFactorNode = edge_copy.get_node(id_)

            mean: SubData = copy.deepcopy(node_copy._data)
            unit_vector: 'SubSizeVector' = VectorFactory.from_dim(node_copy.get_dim()).zeros()

            unit_vector[i] = delta
            plus: T = mean.oplus(unit_vector)
            node_copy.set_value(plus)
            plus_error: 'SubSizeVector' = edge_copy.compute_error_vector()

            unit_vector[i] = - delta
            minus: T = mean.oplus(unit_vector)
            node_copy.set_value(minus)
            minus_error: 'SubSizeVector' = edge_copy.compute_error_vector()
            error = plus_error.array() - minus_error.array()

            column: 'SubSizeVector' = VectorFactory.from_dim(self.get_dim())(
                error / (2 * delta)
            )
            jacobian.append(column.to_list())
        return Matrix(np.array(jacobian).transpose())

    def get_cardinality(self) -> int:
        return len(self.get_nodes())

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = self.get_data().read_rest(words)
        return self._info_matrix.read_rest(words)

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self.get_data().write() + self._info_matrix.write()
        return words

    # copy
    def __copy__(self):
        new = super().__copy__()

        # DataContainer
        new.set_value(self.get_value())
        # FactorEdge
        new._info_matrix = self._info_matrix
        # new._error_vector = self._error_vector
        # new._jacobian = self._jacobian
        # new._hessian = self._hessian
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}

        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        # DataContainer
        new.set_value(copy.deepcopy(self.get_value(), memo))
        # FactorEdge
        new.set_info_matrix(copy.deepcopy(self.get_info_matrix(), memo))
        # new._error_vector = copy.deepcopy(self._error_vector, memo)
        # new._jacobian = copy.deepcopy(self._jacobian, memo)
        # new._hessian = copy.deepcopy(self._hessian, memo)
        return new
