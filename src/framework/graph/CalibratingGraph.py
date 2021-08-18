import copy
import typing as tp
from abc import ABC, abstractmethod

from src.framework.graph.Graph import Edge, Node, Graph, SubNode
from src.framework.graph.types.nodes.ParameterNode import ParameterNode, SubParameterNode
from src.framework.graph.types.nodes.SpatialNode import SubSpatialNode, SpatialNode
from src.framework.math.matrix.square import SubSquare

SubCalibratingGraph = tp.TypeVar('SubCalibratingGraph', bound='CalibratingGraph')
SubCalibratingEdge = tp.TypeVar('SubCalibratingEdge', bound='CalibratingEdge')
SubCalibratingNode = tp.TypeVar('SubCalibratingNode', bound='CalibratingNode')


class CalibratingGraph(Graph):
    _endpoints: tp.Dict[int, SubSpatialNode]
    _parameters: tp.Dict[int, SubParameterNode]
    _parameter_names: tp.List[str]  # parameters names

    def __init__(self):
        super().__init__()
        self._endpoints = {}
        self._parameters = {}
        self._parameter_names = []

    # parameters
    def add_node(self, node: SubNode) -> None:
        if isinstance(node, SpatialNode):
            self.add_endpoint(node)
        elif isinstance(node, ParameterNode):
            name: str = node.get_name()
            if name not in self.get_names():
                self._parameter_names.append(name)
            self.add_parameter(node)
        else:
            super().add_node(node)

    def add_endpoint(self, node: ParameterNode):
        id_: int = node.get_id()
        assert id_ not in self._endpoints, f'{id_}'
        self._endpoints[id_] = node
        super().add_node(node)

    def get_endpoints(self) -> tp.List[SubSpatialNode]:
        return list(self._endpoints.values())

    def add_parameter(self, node: ParameterNode):
        id_: int = node.get_id()
        assert id_ not in self._parameters
        self._parameters[id_] = node
        super().add_node(node)

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return list(self._parameters.values())

    def clear(self) -> None:
        super().clear()
        self._endpoints = {}
        self._parameters = {}
        self._parameter_names = []

    def get_parameter_names(self) -> tp.List[str]:
        return self._parameter_names


T = tp.TypeVar('T')


class CalibratingNode(tp.Generic[T], Node[T]):
    pass


class CalibratingEdge(tp.Generic[T], Edge[T], ABC):
    _num_endpoints: int
    _num_additional: int

    _endpoints: tp.Dict[int, SubSpatialNode]
    _parameters: tp.Dict[int, SubParameterNode]

    def __init__(
            self,
            name: tp.Optional[str] = None,
            nodes: tp.Optional[tp.List[SubNode]] = None,
            measurement: tp.Optional[T] = None,
            info_matrix: tp.Optional[SubSquare] = None
    ):
        assert len(nodes) in (0, self._num_endpoints)

        self._num_additional = 0
        self._endpoints = {}
        self._parameters = {}
        super().__init__(name=name, nodes=nodes, measurement=measurement, info_matrix=info_matrix)

    # attributes
    def get_cardinality(self) -> int:
        return self._num_endpoints + self._num_additional

    def set_num_additional(self, num_additional: int) -> None:
        """ Sets the number of additional (beyond the number of topological) nodes. """
        self._num_additional = num_additional

    @abstractmethod
    def get_delta(self) -> T:
        """ Returns a (spatial) measure (i.e., 'value') inferred by the connected (spatial) nodes. """
        pass

    # override
    def add_node(self, node: SubNode) -> None:
        if isinstance(node, SpatialNode):
            self.add_endpoint(node)
        elif isinstance(node, ParameterNode):
            self.add_parameter(node)
        else:
            super().add_node(node)

    def get_nodes(self) -> tp.List[SubNode]:
        nodes: tp.List[SubNode] = []
        nodes += self.get_endpoints()
        if self.has_parameters():
            nodes += self.get_parameters()
        return nodes

    def remove_node(self, node: SubNode) -> None:
        if isinstance(node, SpatialNode):
            self.remove_endpoint(node)
        elif isinstance(node, ParameterNode):
            self.remove_parameter(node)
        else:
            super().remove_node(node)

    def remove_node_id(self, id_: int) -> None:
        node: SubNode = self.get_node(id_)
        self.remove_node(node)

    # endpoints
    def add_endpoint(self, node: SubSpatialNode):
        assert len(self._endpoints) < self._num_endpoints

        id_: int = node.get_id()
        assert id_ not in self._endpoints
        self._endpoints[id_] = node
        super().add_node(node)

    def get_endpoints(self) -> tp.List[SubSpatialNode]:
        return list(self._endpoints.values())

    def remove_endpoint(self, node: SpatialNode) -> None:
        return self.remove_endpoint_id(node.get_id())

    def remove_endpoint_id(self, id_: int) -> None:
        assert id_ in self._endpoints
        del self._endpoints[id_]

    # parameter
    def add_parameter(self, node: ParameterNode):
        id_: int = node.get_id()
        assert id_ not in self._parameters
        self._parameters[id_] = node
        super().add_node(node)

    def has_parameters(self) -> bool:
        return len(self._parameters) > 0

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return list(self._parameters.values())

    def remove_parameter(self, node: ParameterNode) -> None:
        self.remove_parameter_id(node.get_id())

    def remove_parameter_id(self, id_: int) -> None:
        assert id_ in self._parameters
        del self._parameters[id_]

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = self.get_data().read_rest(words)
        words = self._info_matrix.read_rest(words)
        return words

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self.get_data().write()
        words += self._info_matrix.write()
        return words

    # copy
    def copy_meta_to(self, edge: SubCalibratingEdge) -> SubCalibratingEdge:
        edge = super().copy_meta_to(edge)
        edge._num_additional = self._num_additional
        return edge

    def __copy__(self):
        new = super().__copy__()
        new._num_additional = self._num_additional
        return new

    def __deepcopy__(self, memo: tp.Optional[tp.Dict[int, tp.Any]] = None):
        if memo is None:
            memo = {}
        new = super().__deepcopy__(memo)
        memo[id(self)] = new

        new._num_additional = self._num_additional
        return new
