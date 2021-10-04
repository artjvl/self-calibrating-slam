import typing as tp
from abc import abstractmethod

import numpy as np
from matplotlib import pyplot as plt
from src.framework.graph.parameter.ParameterNodeFactory import ParameterNodeFactory
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.vector import VectorFactory, Vector2

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity
    from src.framework.graph.Graph import SubParameterNode, SubEdge, SubGraph
    from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification
    from src.framework.math.matrix.vector import SubVector
    from src.framework.math.matrix.vector.Vector import SubSizeVector
    from src.framework.math.matrix.square import SubSquare
    from src.framework.simulation.Simulation import SubSimulation

SubPostAnalyser = tp.TypeVar('SubPostAnalyser', bound='PostAnalyser')


class PostAnalyser(object):
    _sim: 'SubSimulation'
    _edges: tp.List['SubGraph']

    def __init__(
            self,
            simulation: 'SubSimulation'
    ):
        self._sim = simulation
        self._edges = []

    def add_edge(
            self,
            edge: 'SubGraph'
    ) -> None:
        self._edges.append(edge)

    def edges(self) -> tp.List['SubGraph']:
        return self._edges

    @abstractmethod
    def post_process(self) -> None:
        pass


SubSpatialBatchAnalyser = tp.TypeVar('SubSpatialBatchAnalyser', bound='SpatialBatchAnalyser')


class SpatialBatchAnalyser(PostAnalyser):
    _name: str
    _init_value: 'Quantity'
    _specification: 'ParameterSpecification'
    _index: int
    _num_batches: int

    def __init__(
            self,
            sim: 'SubSimulation',
            name: str,
            value: 'Quantity',
            specification: 'ParameterSpecification',
            num_batches: int,
            index: int = 0
    ):
        super().__init__(sim)
        self._name = name
        self._init_value = value
        self._specification = specification
        self._index = index
        self._num_batches = num_batches

    def post_process(self) -> None:
        # calculate edge centres
        edges: tp.List['SubGraph'] = self.edges()
        averages: np.ndarray = np.zeros((2, len(edges)))
        for i, edge in enumerate(edges):
            endpoints: tp.List['SubGraph'] = edge.get_endpoints()
            translations: np.ndarray = np.zeros((2, len(endpoints)))
            for j, endpoint in enumerate(endpoints):
                translations[:, j] = endpoint.get_value().get_translation().array().flatten()
            averages[:, i] = np.mean(translations, axis=1)

        # perform k-means clustering
        from sklearn.cluster import KMeans
        k = KMeans(n_clusters=self._num_batches, random_state=0)
        # k = KMeans(n_clusters=self._num_batches, init='k-means++', max_iter=300, n_init=10, random_state=0)
        k.fit_predict(averages.transpose())

        # create parameters
        parameters: tp.List['SubParameterNode'] = []
        for i in range(self._num_batches):
            parameter: 'SubParameterNode' = ParameterNodeFactory.from_value(
                self._init_value,
                name = self._name,
                specification=self._specification,
                index=self._index
            )
            translation: Vector2 = Vector2(k.cluster_centers_[i, :])
            parameter.set_translation(translation)
            self._sim.add_node(parameter)
            parameters.append(parameter)

        # assign parameters
        label_dict: tp.Dict[int, int] = {}
        label_counter: int = 0
        for i, edge in enumerate(edges):
            label: int = k.labels_[i]
            if label not in label_dict:
                label_dict[label] = label_counter
                label_counter += 1
            index: int = label_dict[label]
            parameter: 'SubParameterNode' = parameters[index]
            edge.add_parameter(parameter)

        centres: np.ndarray = k.cluster_centers_.transpose()
        fig, ax = plt.subplots()
        ax.scatter(averages[0, :], averages[1, :])
        ax.scatter(centres[0, :], centres[1, :], s=300, c='red')
        fig.show()
        print('done')


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
        assert vector.dim() == self._dim
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
            simulation: 'SubSimulation',
            window_size: int
    ):
        super().__init__(simulation)
        self._window_size = window_size

    def calculate_variances(self) -> VectorList:
        window: int = self._window_size
        edges: tp.List['SubEdge'] = self.edges()
        dim: int = edges[0].get_dim()
        vector_type: tp.Type['SubSizeVector'] = VectorFactory.from_dim(dim)
        vector_list: VectorList = VectorList(dim)

        left: int = int(np.floor(window / 2))
        right: int = window - left

        for i, edge in enumerate(edges):
            edge_window: tp.List[edges] = edges[np.maximum(0, i - left + 1): i + right + 1]
            error_vectors: tp.List['SubVector'] = [edge.error_vector() for edge in edge_window]

            variance_vector: 'SubSizeVector' = vector_type.zeros()
            for i in range(dim):
                errors: tp.List[float] = [error_vector[i] for error_vector in error_vectors]
                variance_vector[i] = float(np.var(errors))
            vector_list.append(variance_vector)
        vector_list.plot()
        return vector_list

    def post_process(self) -> None:
        edges: tp.List['SubGraph'] = self.edges()
        dim: int = edges[0].get_dim()
        matrix_type: tp.Type['SubSquare'] = SquareFactory.from_dim(dim)

        vector_list: VectorList = self.calculate_variances()
        for i, edge in enumerate(edges):
            cov_matrix: 'SubSquare' = matrix_type.from_diagonal(vector_list.get(i).to_list())
            edge.set_cov_matrix(cov_matrix)
        return None
