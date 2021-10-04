import copy
import typing as tp
from abc import abstractmethod

import numpy as np
from src.framework.graph.data import DataFactory
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.vector import VectorFactory
from src.framework.math.matrix.vector.Vector import Vector
from src.framework.ppg.parameter.ParameterSpecification import ParameterDict

if tp.TYPE_CHECKING:
    from src.framework.graph.data import SubData, SubDataSymmetric
    from src.framework.optimiser.Optimiser import Optimiser
    from src.framework.ppg.Measurement import SubMeasurement
    from src.framework.ppg.parameter.ParameterSpecification import ParameterSpecification
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.vector import SubVector, SubSizeVector, Vector2, Vector3
    from src.framework.math.matrix.square import SubSquare

SubElement = tp.TypeVar('SubElement', bound='Element')
SubDataContainer = tp.TypeVar('SubDataContainer', bound='DataContainer')
SubNode = tp.TypeVar('SubNode', bound='Node')
SubSpatialNode = tp.TypeVar('SubSpatialNode', bound='SpatialNode')
SubParameterNode = tp.TypeVar('SubParameterNode', bound='ParameterNode')
SubNodeContainer = tp.TypeVar('SubNodeContainer', bound='NodeContainer')
SubEdge = tp.TypeVar('SubEdge', bound='Edge')
SubNodeEdge = tp.Union[SubNode, SubEdge]
SubGraph = tp.TypeVar('SubGraph', bound='Graph')

T = tp.TypeVar('T')


class Element(object):
    _name: str

    def __init__(
            self,
            name: tp.Optional[str],
            **kwargs
    ):
        super().__init__(**kwargs)
        if name is None:
            name = self.__class__.__name__
        self._name = name

    def name(self) -> str:
        return self._name

    @abstractmethod
    def is_equivalent(self, other: SubElement) -> bool:
        pass

    def copy_attributes_to(self, other: SubElement) -> SubElement:
        assert self.is_equivalent(other)
        other._name = self._name
        return other


class DataContainer(tp.Generic[T]):
    _type: tp.Type[T]
    _data: 'SubData'

    def __init__(
            self,
            value: tp.Optional[T] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._data = DataFactory.from_type(self._type)(value)

    @classmethod
    def dim(cls) -> int:
        return DataFactory.from_type(cls._type).dim()

    def data(self) -> 'SubData':
        return self._data

    def has_value(self) -> bool:
        return self._data.has_value()

    def get_value(self) -> T:
        assert self.has_value()
        return self._data.get_value()

    def set_value(self, value: T) -> None:
        self._data.set_value(value)

    def to_vector(self) -> 'SubSizeVector':
        return self._data.to_vector()

    def set_from_vector(self, vector: 'SubSizeVector') -> None:
        self._data.set_from_vector(vector)

    def set_zero(self) -> None:
        self.set_from_vector(VectorFactory.from_dim(self.dim()).zeros())

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        return self._data.read_rest(words)

    def write(self) -> tp.List[str]:
        return self._data.write()


class Node(Element, tp.Generic[T], DataContainer[T]):
    _id: int
    _timestep: int
    _is_fixed: bool
    _truth: tp.Optional[SubNode]

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[T] = None,
            timestep: int = 0
    ):
        super().__init__(name=name, value=value)

        # attributes
        self._id = id_
        self._timestep = timestep
        self._is_fixed = False
        self._truth = None

    def id(self) -> int:
        return self._id

    def set_timestep(self, timestep: int) -> None:
        self._timestep = timestep

    def get_timestep(self) -> int:
        return self._timestep

    def fix(self, is_fixed: bool = True) -> None:
        self._is_fixed = is_fixed

    def is_fixed(self) -> bool:
        return self._is_fixed

    # truth
    def is_similar(self, other: SubEdge) -> bool:
        self_id: int = self.id()
        other_id: int = other.id()
        return self_id == other_id

    def has_truth(self) -> bool:
        return self._truth is not None

    def assign_truth(self, edge: SubEdge):
        assert not self.has_truth()
        assert self.is_similar(edge)
        self._truth = edge

    # copy
    def is_equivalent(self, other: SubNode) -> bool:
        has_same_type: bool = type(other) == type(self)
        has_same_id: bool = other.id() == self.id()
        return has_same_type and has_same_id

    def copy_attributes_to(self, other: SubNode) -> SubNode:
        super().copy_attributes_to(other)
        other._timestep = self._timestep
        other._truth = self._truth
        return other

    def __copy__(self) -> SubNode:
        cls = self.__class__
        new = cls.__new__(cls)
        new._id = self._id
        new._is_fixed = self._is_fixed
        new._data = copy.copy(self._data)
        self.copy_attributes_to(new)
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None) -> SubNode:
        if memo is None:
            memo = {}
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        new._id = self._id
        new._is_fixed = self._is_fixed
        new._data = copy.deepcopy(self._data, memo)
        self.copy_attributes_to(new)
        return new


class SpatialNode(tp.Generic[T], Node[T]):
    _ate2: tp.Optional[float]

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[T] = None,
            timestep: int = 0
    ):
        super().__init__(
            name, id_,
            value=value, timestep=timestep
        )
        self._ate2 = None

    # metrics
    def set_value(self, value: T) -> None:
        super().set_value(value)
        self._set_metrics()

    def set_from_vector(self, vector: 'SubSizeVector') -> None:
        super().set_from_vector(vector)
        self._set_metrics()

    def assign_truth(self, edge: SubEdge):
        super().assign_truth(edge)
        self._set_metrics()

    def _set_metrics(self) -> None:
        if self.has_truth():
            self._ate2 = self._compute_ate2()

    @abstractmethod
    def _compute_ate2(self) -> tp.Optional[float]:
        pass

    @abstractmethod
    def translation(self) -> 'Vector2':
        pass

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = super().read(words)
        self._set_metrics()
        return words

    # copy
    def __copy__(self) -> SubSpatialNode:
        new = super().__copy__()
        new._ate2 = self._ate2
        self.copy_attributes_to(new)
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None) -> SubSpatialNode:
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new
        new._ate2 = self._ate2
        return new


class ParameterNode(tp.Generic[T], Node[T]):
    _specification: 'ParameterSpecification'
    _index: int
    _translation: tp.Optional['Vector2']

    def __init__(
            self,
            name: tp.Optional[str],
            id_: int,
            value: tp.Optional[T],
            specification: 'ParameterSpecification',
            timestep: int = 0,
            index: int = 0
    ):
        super().__init__(name, id_, value, timestep)
        self.set_specification(specification)
        self._index = index
        self._translation = None

    @abstractmethod
    def compose(
            self,
            measurement: 'SE2',
            is_inverse: bool = False
    ) -> 'SubMeasurement':
        pass

    # attributes
    def set_specification(self, specification: 'ParameterSpecification') -> None:
        self._specification = specification

    def get_specification(self) -> 'ParameterSpecification':
        return self._specification

    def index(self) -> int:
        return self._index

    def reinitialise(self) -> 'SubSizeVector':
        vector: 'SubSizeVector' = self.to_vector()
        self.reset()
        return vector

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def to_vector3(self) -> 'Vector3':
        pass

    # translation
    def has_translation(self) -> bool:
        return self._translation is not None

    def set_translation(self, translation: 'Vector2') -> None:
        self._translation = translation

    def get_translation(self) -> 'Vector2':
        assert self.has_translation()
        return self._translation

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        self._specification = ParameterDict.from_string(words[0])
        return super().read(words[1:])

    def write(self) -> tp.List[str]:
        return [ParameterDict.from_specification(self._specification)] + super().write()

    # copy
    def copy_attributes_to(self, node: SubParameterNode) -> SubParameterNode:
        node = super().copy_attributes_to(node)
        node._specification = self._specification
        node._index = self._index
        node._translation = self._translation
        return node


class NodeContainer(Element):
    _nodes: tp.Dict[int, SubNode]
    _spatial_nodes: tp.Dict[int, SpatialNode]
    _parameter_nodes: tp.Dict[int, ParameterNode]

    def __init__(
            self,
            name: tp.Optional[str],
            **kwargs
    ):
        super().__init__(name, **kwargs)
        self._nodes = {}
        self._spatial_nodes = {}
        self._parameter_nodes = {}

    # nodes
    def add_node(self, node: SubNode) -> None:
        id_: int = node.id()
        assert id_ not in self._nodes
        self._nodes[id_] = node
        if isinstance(node, SpatialNode):
            self._spatial_nodes[id_] = node
        else:
            assert isinstance(node, ParameterNode)
            self._parameter_nodes[id_] = node

    def contains_node_id(self, id_: int) -> bool:
        return id_ in self._nodes

    def get_node(self, id_: int) -> SubNode:
        assert self.contains_node_id(id_)
        return self._nodes[id_]

    def get_nodes(self) -> tp.List[SubNode]:
        return list(self._nodes.values())

    def get_active_nodes(self) -> tp.List[SubNode]:
        return [node for node in self.get_nodes() if not node.is_fixed()]

    def get_spatial_nodes(self) -> tp.List[SubSpatialNode]:
        return list(self._spatial_nodes.values())

    def get_parameter_nodes(self) -> tp.List[SubParameterNode]:
        return list(self._parameter_nodes.values())

    # clear
    def clear(self) -> None:
        self._nodes = {}
        self._spatial_nodes = {}
        self._parameter_nodes = {}

    # copy
    def is_similar(self, other: SubNodeContainer) -> bool:
        self_spatial_ids: tp.List[int] = [node.id() for node in self.get_spatial_nodes()]
        other_spatial_ids: tp.List[int] = [node.id() for node in other.get_spatial_nodes()]
        return other_spatial_ids == self_spatial_ids

    def is_equivalent(self, other: SubNodeContainer) -> bool:
        self_node_ids: tp.List[int] = [node.id() for node in self.get_nodes()]
        other_node_ids: tp.List[int] = [node.id() for node in other.get_nodes()]
        return other_node_ids == self_node_ids

    def __copy__(self) -> SubNodeContainer:
        cls = self.__class__
        new = cls.__new__(cls)
        new._nodes = copy.copy(self._nodes)
        new._spatial_nodes = copy.copy(self._spatial_nodes)
        new._parameter_nodes = copy.copy(self._parameter_nodes)
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None) -> SubNodeContainer:
        if memo is None:
            memo = {}
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        new._nodes = copy.deepcopy(self._nodes, memo)
        new._spatial_nodes = copy.deepcopy(self._spatial_nodes, memo)
        new._parameter_nodes = copy.deepcopy(self._parameter_nodes, memo)
        return new


class Edge(tp.Generic[T], DataContainer[T], NodeContainer):
    _cardinality: int
    _info_matrix: 'SubDataSymmetric'
    _truth: tp.Optional[SubNode]

    # metrics
    _error_vector: tp.Optional['SubSizeVector']
    _rpet2: tp.Optional[float]
    _rper2: tp.Optional[float]

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[T] = None,
            info_matrix: tp.Optional['SubSquare'] = None,
            nodes: tp.Optional[tp.List[SubNode]] = None
    ):
        super().__init__(name=name, value=value)
        if info_matrix is None:
            info_matrix = SquareFactory.from_dim(self.dim()).identity()
        assert info_matrix.dim() == self.dim()
        self._info_matrix = DataFactory.from_value(info_matrix)
        self._truth = None

        # metrics
        self._error_vector = None
        self._rpet2 = None
        self._rper2 = None

        # nodes
        if nodes is not None:
            for node in nodes:
                self.add_node(node)

    @classmethod
    def cardinality(cls) -> int:
        return cls._cardinality

    # measurement model
    @abstractmethod
    def estimate(self) -> T:
        pass

    @abstractmethod
    def delta(self) -> T:
        pass

    # info matrix
    def get_info_matrix(self) -> 'SubSquare':
        return self._info_matrix.get_value()

    def set_info_matrix(self, info_matrix: 'SubSquare') -> None:
        self._info_matrix.set_value(info_matrix)

    # truth
    def has_truth(self) -> bool:
        return self._truth is not None

    def assign_truth(self, edge: SubEdge):
        assert not self.has_truth()
        assert self.is_similar(edge)
        self._truth = edge
        self._set_metrics()

    # metrics
    def add_node(self, node: SubNode) -> None:
        super().add_node(node)
        self._set_metrics()

    def remove_node_id(self, id_) -> None:
        assert self.contains_node_id(id_)
        del self._nodes[id_]
        if id_ in self._spatial_nodes:
            del self._spatial_nodes[id_]
        else:
            assert id_ in self._parameter_nodes
            del self._parameter_nodes[id_]
        self._set_metrics()

    def set_value(self, value: T) -> None:
        super().set_value(value)
        self._set_metrics()

    def set_from_vector(self, vector: 'SubSizeVector') -> None:
        super().set_from_vector(vector)
        self._set_metrics()

    def _set_metrics(self) -> None:
        if self.has_value() and self._is_complete():
            self._error_vector = self._compute_error_vector()
            if self.has_truth():
                self._rpet2 = self._compute_rpe_translation2()
                self._rper2 = self._compute_rpe_rotation2()

    def _is_complete(self) -> bool:
        return len(self.get_spatial_nodes()) == self.cardinality()

    @abstractmethod
    def _compute_error_vector(self) -> 'SubSizeVector':
        pass

    @abstractmethod
    def _compute_rpe_translation2(self) -> tp.Optional[float]:
        pass

    @abstractmethod
    def _compute_rpe_rotation2(self) -> tp.Optional[float]:
        pass

    def error_vector(self) -> 'SubSizeVector':
        assert self._is_complete()
        return self._error_vector

    def rpe_translation2(self) -> tp.Optional[float]:
        assert self.has_truth() and self._is_complete()
        return self._rpet2

    def rpe_rotation2(self) -> tp.Optional[float]:
        assert self.has_truth() and self._is_complete()
        return self._rper2

    def cost(self) -> float:
        return self.mahalanobis_distance(self.error_vector(), self._info_matrix)

    @staticmethod
    def mahalanobis_distance(
            vector: 'SubSizeVector',
            matrix: 'SubSquare'
    ) -> float:
        assert vector.dim() == matrix.dim()
        vector_array: np.ndarray = vector.array()
        return float(vector_array.transpose() @ matrix.array() @ vector_array)

    # timestep
    def timestep(self) -> int:
        timesteps: tp.List[int] = [node.get_timestep() for node in self.get_nodes()]
        return max(timesteps)

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = self.data().read_rest(words)
        words = self._info_matrix.read_rest(words)
        self._set_metrics()
        return words

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self.data().write() + self._info_matrix.write()
        return words

    # copy
    def copy_attributes_to(self, other: SubEdge) -> SubEdge:
        super().copy_attributes_to(other)
        other._truth = self._truth
        return other

    def __copy__(self) -> SubEdge:
        new = super().__copy__()
        new._data = copy.copy(self._data)
        new._info_matrix = copy.copy(self._info_matrix)
        new._error_vector = self._error_vector
        new._rpet2 = self._rpet2
        new._rper2 = self._rper2
        self.copy_attributes_to(new)
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None) -> SubEdge:
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new
        new._data = copy.deepcopy(self._data, memo)
        new._info_matrix = copy.deepcopy(self._info_matrix, memo)
        new._error_vector = self._error_vector
        new._rpet2 = self._rpet2
        new._rper2 = self._rper2
        self.copy_attributes_to(new)
        return new


class Graph(NodeContainer):
    # elements
    _by_type: tp.Dict[tp.Type[SubNodeEdge], tp.List[SubNodeEdge]]
    _by_name: tp.Dict[str, tp.List[SubNodeEdge]]
    _edges: tp.List[SubEdge]

    # references
    _previous: tp.Optional[SubGraph]
    _truth: tp.Optional[SubGraph]
    _atol: float

    def __init__(
            self,
            name: tp.Optional[str] = None
    ):
        super().__init__(name=name)
        self._by_type = {}
        self._by_name = {}
        self._edges = []
        self._previous = None
        self._truth = None
        self._atol = 1e-6

    # elements
    def has_name(self, name: str) -> bool:
        return name in self._by_name

    def get_of_name(self, name: str) -> tp.List[SubNodeEdge]:
        assert self.has_name(name)
        return self._by_name[name]

    def get_type_of_name(self, name: str) -> tp.Type[SubNodeEdge]:
        return type(self.get_of_name(name)[0])

    def get_names(self) -> tp.List[str]:
        return list(self._by_name.keys())

    def has_type(self, type_: tp.Type[SubNodeEdge]) -> bool:
        return type_ in self._by_type

    def get_of_type(self, type_: tp.Type[SubNodeEdge]) -> tp.List[SubNodeEdge]:
        assert self.has_type(type_)
        return self._by_type[type_]

    def get_types(self) -> tp.List[tp.Type[SubNodeEdge]]:
        return list(self._by_type.keys())

    def get_node_types(self) -> tp.List[tp.Type[SubNode]]:
        return [type_ for type_ in self.get_types() if issubclass(type_, Node)]

    def get_edge_types(self) -> tp.List[tp.Type[SubEdge]]:
        return [type_ for type_ in self.get_types() if issubclass(type_, Edge)]

    def get_elements(self) -> tp.List[SubNodeEdge]:
        return self.get_nodes() + self.get_edges()

    def get_edges(self) -> tp.List[SubEdge]:
        return self._edges

    def add_node(self, node: SubNode) -> None:
        super().add_node(node)
        self._add_element(node)

    def add_edge(self, edge: SubEdge):
        for node in edge.get_nodes():
            assert self.contains_node_id(node.id())
        self._edges.append(edge)
        self._add_element(edge)

    def _add_element(self, element: SubNodeEdge) -> None:
        element_type: tp.Type[SubNodeEdge] = type(element)
        if not self.has_type(element_type):
            self._by_type[element_type] = []
        self._by_type[element_type].append(element)

        element_name: str = element.name()
        if not self.has_name(element_name):
            self._by_name[element_name] = []
        else:
            assert type(element) == self.get_type_of_name(element_name)
        self._by_name[element_name].append(element)

    # optimise
    def optimise(
            self,
            optimiser: 'Optimiser',
            cost_threshold: tp.Optional[float] = None
    ) -> tp.Optional[SubGraph]:
        parameters: tp.List[SubParameterNode] = self.get_parameter_nodes()
        vectors: tp.List['SubSizeVector'] = []
        for parameter in parameters:
            vector: 'SubSizeVector' = parameter.reinitialise()
            vectors.append(vector)
        if cost_threshold is None:
            cost_threshold = self.cost()

        solution: tp.Optional[SubGraph] = optimiser.instance_optimise(self)
        if solution is not None:

            # cost below cost_threshold is considered optimal
            cost: float = solution.cost()
            if cost < cost_threshold:
                return self.accept_solution(solution)

            # else: reset parameters and try again
            for parameter in parameters:
                parameter.fix()
            solution = optimiser.instance_optimise(self)

            if solution is not None:
                return self.accept_solution(solution)

            # revert parameters
            for i, parameter in enumerate(parameters):
                parameter.fix(is_fixed=False)
                parameter.set_from_vector(vectors[i])

    def accept_solution(self, solution: SubGraph) -> SubGraph:
        self.from_vector(solution.to_vector())
        if self.has_previous():
            solution.set_previous(self.get_previous())
        return solution

    # vector
    def to_vector(self) -> 'SubVector':
        vector_list: tp.List[float] = []
        node: SubNode
        for node in self.get_nodes():
            vector_list += node.to_vector().to_list()
        return Vector(vector_list)

    def from_vector(self, vector: 'SubVector') -> None:
        vector_list: tp.List[float] = vector.to_list()
        index: int = 0
        for node in self.get_nodes():
            dim: int = node.dim()
            segment: tp.List[float] = vector_list[index: index + dim]
            assert len(segment) == dim
            node.set_from_vector(VectorFactory.from_list(segment))
            index += dim
        assert index == len(vector_list)

    # truth
    def has_truth(self) -> bool:
        return self._truth is not None

    def get_truth(self) -> SubGraph:
        assert self.has_truth()
        return self._truth

    def assign_truth(
            self,
            graph: SubGraph
    ) -> None:
        assert graph.is_consistent()
        assert self.is_similar(graph)
        assert not self.has_truth()
        self._truth = graph

        # nodes
        for node in self.get_nodes():
            id_: int = node.id()
            if self.contains_node_id(id_):
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
                is_eligible = edge.is_similar(truth_edge)
            edge.assign_truth(truth_edge)

    # subgraphs
    def previous_depth(self) -> int:
        graph: SubGraph = self
        depth: int = 1
        while graph.has_previous():
            graph = graph.get_previous()
            depth += 1
        return depth

    def set_previous(self, previous: SubGraph) -> None:
        self._previous = previous

    def has_previous(self) -> bool:
        return self._previous is not None

    def get_previous(self) -> SubGraph:
        assert self.has_previous()
        return self._previous

    def subgraphs(self) -> tp.List[SubGraph]:
        graph: SubGraph = self
        graphs: tp.List[SubGraph] = [graph]
        while graph.has_previous():
            graph = graph.get_previous()
            graphs.append(graph)
        return graphs

    def find_subgraphs(self) -> tp.List[SubGraph]:
        assert not self.has_previous()
        graph: SubGraph = self.__class__()
        subgraphs: tp.List[SubGraph] = []

        # initialise an empty node-set and edge-iterator
        node_set: tp.Set[SubGraph] = set()
        edge_iter: iter = iter(self.get_edges())
        edge: tp.Optional[SubEdge] = next(edge_iter)

        is_completed: bool = False
        while not is_completed:
            # add nodes connected to current edge to node-set
            edges_to_add: tp.List[SubEdge] = []
            node_set.update(edge.get_spatial_nodes())

            # find all edges contained in the current node-set
            is_contained = True
            while is_contained:
                edges_to_add.append(edge)
                edge = next(edge_iter, None)
                if edge is not None:
                    is_contained = (set(edge.get_spatial_nodes()) <= node_set)
                else:
                    is_completed = True
                    is_contained = False

            # copy graph
            if not is_completed:
                timestep: int = len(subgraphs)
                for edge_to_add in edges_to_add:
                    for node in edge_to_add.get_nodes():
                        if not graph.contains_node_id(node.get_id()):
                            node.set_timestep(timestep)
                            graph.add_node(node)
                    graph.add_edge(edge_to_add)
                subgraphs.append(copy.copy(graph))
        subgraphs.append(self)

        # store subgraphs
        for i in range(1, len(subgraphs)):
            subgraphs[i]._previous = subgraphs[i - 1]

        # find truth subgraphs
        if self.has_truth():
            truth_subgraphs: tp.List[SubGraph] = self.get_truth().find_subgraphs()
            assert len(truth_subgraphs) == len(subgraphs)

            for i, subgraph in enumerate(subgraphs):
                truth_subgraph: SubGraph = truth_subgraphs[i]
                subgraph._truth = truth_subgraph

        return subgraphs

    @staticmethod
    def from_subgraphs(subgraphs: tp.List[SubGraph]) -> SubGraph:
        for i in range(1, len(subgraphs)):
            subgraphs[i]._previous = subgraphs[i - 1]
        return subgraphs[-1]

    # metrics
    def set_atol(self, atol: float) -> None:
        self._atol = atol

    def is_consistent(self) -> bool:
        return bool(np.isclose(self.cost(), 0., atol=self._atol))

    def cost(self) -> float:
        error: float = 0.
        for edge in self.get_edges():
            error += edge.cost()
        return error

    def ate(self) -> float:
        te2: float = 0
        count: int = 0
        node: SubNode
        for node in self.get_spatial_nodes():
            node_ate2 = node.ate2()
            if node_ate2 is not None:
                te2 += node_ate2
                count += 1
        ate: float = np.sqrt(te2 / count)
        return ate

    def rpe_translation(self) -> float:
        rpe2: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.rpe_translation2()
            if edge_rpe2 is not None:
                rpe2 += edge_rpe2
                count += 1
        rpe_translation: float = np.sqrt(rpe2 / count)
        return rpe_translation

    def rpe_rotation(self) -> float:
        rpe: float = 0
        count: int = 0
        edge: SubEdge
        for edge in self.get_edges():
            edge_rpe2 = edge.rpe_rotation2()
            if edge_rpe2 is not None:
                rpe += edge_rpe2
                count += 1
        rpe_rotation: float = rpe / count
        return rpe_rotation

    # clear
    def clear(self) -> None:
        super().clear()
        self._by_name = {}
        self._by_type = {}
        self._edges = []

    # copy
    def is_similar(self, graph: SubGraph) -> bool:
        """
        Similarity: the graph contains identical connectivity between spatial nodes.
        """
        graph_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(node.id() for node in edge.get_spatial_nodes()) for edge in graph.get_edges() if edge.get_spatial_nodes()]
        self_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(node.id() for node in edge.get_spatial_nodes()) for edge in self.get_edges() if edge.get_spatial_nodes()]
        has_similar_edges: bool = graph_edges_ids == self_edges_ids
        has_equivalent_endpoints: bool = super().is_similar(graph)
        return has_similar_edges and has_equivalent_endpoints

    def is_equivalent(self, graph: SubGraph) -> bool:
        """
        Equivalence: the graph contains identical connectivity.
        """
        graph_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(node.id() for node in edge.get_nodes()) for edge in graph.get_edges()]
        self_edges_ids: tp.List[tp.Tuple[int, ...]] = [tuple(node.id() for node in edge.get_nodes()) for edge in self.get_edges()]
        has_equivalent_edges: bool = graph_edges_ids == self_edges_ids
        has_equivalent_nodes: bool = super().is_equivalent(graph)
        return has_equivalent_edges and has_equivalent_nodes

    def copy_attributes_to(self, other: SubGraph) -> SubGraph:
        super().copy_attributes_to(other)
        other._previous = self._previous
        other._truth = self._truth
        other._atol = self._atol
        return other

    def __copy__(self) -> SubEdge:
        new = super().__copy__()
        new._by_type = {type_: copy.copy(elements) for (type_, elements) in self._by_type.items()}
        new._by_name = {name: copy.copy(elements) for (name, elements) in self._by_name.items()}
        new._edges = copy.copy(self._edges)
        self.copy_attributes_to(new)
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None) -> SubEdge:
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new
        new._by_type = {type_: copy.deepcopy(elements, memo) for (type_, elements) in self._by_type.items()}
        new._by_name = {name: copy.deepcopy(elements, memo) for (name, elements) in self._by_name.items()}
        new._edges = copy.deepcopy(self._edges, memo)
        self.copy_attributes_to(new)
        return new
