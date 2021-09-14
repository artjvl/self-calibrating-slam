import typing as tp
from abc import abstractmethod

import numpy as np
from matplotlib import pyplot as plt
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.vector import VectorFactory

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingEdge
    from src.framework.graph.Graph import SubEdge
    from src.framework.graph.types.nodes.ParameterNode import ParameterSpecification
    from src.framework.math.matrix.vector import SubVector
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.math.matrix.square import SubSquare

SubPostAnalyser = tp.TypeVar('SubPostAnalyser', bound='PostAnalyser')


class PostAnalyser(object):
    _edges: tp.List['SubCalibratingEdge']

    def __init__(self):
        self._edges = []

    def add_edge(
            self,
            edge: 'SubCalibratingEdge'
    ) -> None:
        self._edges.append(edge)

    def get_edges(self) -> tp.List['SubCalibratingEdge']:
        return self._edges

    @abstractmethod
    def post_process(self) -> None:
        pass


SubSpatialBatchAnalyser = tp.TypeVar('SubSpatialBatchAnalyser', bound='SpatialBatchAnalyser')


class SpatialBatchAnalyser(PostAnalyser):
    _name: str
    _specification: 'ParameterSpecification'


    _batch_size: int

    def __init__(
            self,
            name: str,
            specification: 'ParameterSpecification',
            batch_size: int,
            index: int = 0
    ):
        super().__init__()
        self._name = name
        self._specification = specification
        self._batch_size = batch_size

    def post_process(self) -> None:
        pass


SubVarianceAnalyser = tp.TypeVar('SubVarianceAnalyser', bound='VarianceAnalyser')


class VectorList(object):
    _dim: int
    _data: tp.List['SubSizeVector']

    def __init__(
            self,
            dim: int
    ):
        self._dim = dim
        self._data = []

    def append(self, vector: 'SubSizeVector') -> None:
        assert vector.get_dim() == self._dim
        self._data.append(vector)

    def list(self) -> tp.List['SubSizeVector']:
        return self._data

    def get(self, index) -> 'SubSizeVector':
        assert index < self.length()
        return self._data[index]

    def length(self) -> int:
        return len(self._data)

    def plot(self) -> None:
        dim: int = self._dim
        lists: tp.List[tp.List[float]] = self.to_lists()
        fig, axes = plt.subplots(dim, 1)
        for i, ax in enumerate(np.array(axes).flatten()):
            ax.plot(lists[i])
        fig.show()

    def to_lists(self) -> tp.List[tp.List[float]]:
        dim: int = self._dim
        lists: tp.List[tp.List[float]] = [[] for _ in range(dim)]
        for vector in self._data:
            for i in range(dim):
                lists[i].append(vector[i])
        return lists


class VarianceAnalyser(PostAnalyser):
    _window_size: int

    def __init__(
            self,
            window_size: int
    ):
        super().__init__()
        self._window_size = window_size

    def calculate_variances(self) -> VectorList:
        window: int = self._window_size
        edges: tp.List['SubEdge'] = self.get_edges()
        dim: int = edges[0].get_dim()
        vector_type: tp.Type['SubSizeVector'] = VectorFactory.from_dim(dim)
        vector_list: VectorList = VectorList(dim)

        left: int = int(np.floor(window / 2))
        right: int = window - left

        for i, edge in enumerate(edges):
            edge_window: tp.List[edges] = edges[np.maximum(0, i - left + 1): i + right + 1]
            error_vectors: tp.List['SubVector'] = [edge.get_error_vector() for edge in edge_window]

            variance_vector: 'SubSizeVector' = vector_type.zeros()
            for i in range(dim):
                errors: tp.List[float] = [error_vector[i] for error_vector in error_vectors]
                variance_vector[i] = float(np.var(errors))
            vector_list.append(variance_vector)
        vector_list.plot()
        return vector_list

    def post_process(self) -> None:
        edges: tp.List['SubCalibratingEdge'] = self.get_edges()
        dim: int = edges[0].get_dim()
        matrix_type: tp.Type['SubSquare'] = SquareFactory.from_dim(dim)

        vector_list: VectorList = self.calculate_variances()
        for i, edge in enumerate(edges):
            cov_matrix: 'SubSquare' = matrix_type.from_diagonal(vector_list.get(i).to_list())
            edge.set_cov_matrix(cov_matrix)
        return None
