import typing as tp
from abc import ABC, abstractmethod

import numpy as np
from src.framework.graph.Graph import Edge, SubNode, Node, Graph
from src.framework.graph.types.nodes.InformationNode import InformationNode, SubInformationNode
from src.framework.graph.types.nodes.ParameterNode import ParameterNode, SubParameterNode
from src.framework.graph.types.nodes.SpatialNode import SubSpatialNode, SpatialNode
from src.framework.math.matrix.square import SquareFactory
from src.framework.math.matrix.square import SubSquare
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector import VectorFactory

SubCalibratingGraph = tp.TypeVar('SubCalibratingGraph', bound='CalibratingGraph')
SubCalibratingEdge = tp.TypeVar('SubCalibratingEdge', bound='CalibratingEdge')


class CalibratingGraph(Graph):

    _parameters: tp.Dict[str, tp.List[SubParameterNode]]

    def __init__(self):
        super().__init__()
        self._parameters = {}

    def add_node(self, node: SubNode) -> None:
        if isinstance(node, ParameterNode):
            name: str = node.get_name()
            if name not in self._parameters:
                self._parameters[name] = []
            self._parameters[name].append(node)
        super().add_node(node)

    def get_parameter_names(self) -> tp.List[str]:
        return list(self._parameters.keys())

    def get_parameters(self, name: str) -> tp.List[SubParameterNode]:
        assert name in self._parameters
        return self._parameters[name]

    def copy_properties(self, graph: SubCalibratingGraph) -> SubCalibratingGraph:
        super().copy_properties(graph)
        parameters: tp.Dict[str, tp.List[SubParameterNode]] = {}
        for name, nodes in self._parameters.items():
            for node in nodes:
                new_node: SubParameterNode = graph.get_node(node.get_id())
                new_node.set_name(node.get_name())
                if name not in parameters:
                    parameters[name] = []
                parameters[name].append(new_node)
        graph._parameters = parameters
        return graph


T = tp.TypeVar('T')


class CalibratingEdge(tp.Generic[T], Edge[T], ABC):

    _num_topological: int
    _num_additional: int

    _endpoints: tp.List[SubSpatialNode]
    _parameters: tp.List[SubParameterNode]
    _info_node: tp.Optional[SubInformationNode]

    def __init__(
            self,
            value: tp.Optional[T] = None,
            info_matrix: tp.Optional[SubSquare] = None,
            *nodes: SubNode
    ):
        assert len(nodes) in (0, self._num_topological)

        self._num_additional = 0
        self._endpoints = []
        self._parameters = []
        self._info_node = None
        super().__init__(value, info_matrix, *nodes)

    # attributes
    def get_cardinality(self) -> int:
        return self._num_topological + self._num_additional

    def set_num_additional(self, num_additional: int) -> None:
        """ Sets the number of additional (beyond the number of topological) nodes. """
        self._num_additional = num_additional

    @abstractmethod
    def get_value(self) -> T:
        """ Returns a (topological) measure (i.e., 'value') inferred by the connected (topological) nodes. """
        pass

    # override
    def error_vector(self) -> SubVector:
        error_vector: SubVector = self.compute_error_vector()
        if self.has_info_node():
            info_diagonal: SubVector = self.get_info_node().get_value()
            error_vector: SubVector = VectorFactory.from_dim(self.get_dim())(
                np.multiply(np.sqrt(info_diagonal.array()), error_vector.array())
            )
        return error_vector

    def add_node(self, node: SubNode) -> None:
        assert isinstance(node, (SpatialNode, ParameterNode, InformationNode))
        if isinstance(node, SpatialNode):
            self.add_endpoint(node)
        elif isinstance(node, ParameterNode):
            self.add_parameter(node)
        else:
            self.add_info_node(node)

    def get_nodes(self) -> tp.List[SubNode]:
        nodes: tp.List[SubNode] = []
        nodes += self.get_endpoints()
        if self.has_parameters():
            nodes += self.get_parameters()
        if self.has_info_node():
            nodes += [self.get_info_node()]
        return nodes

    # endpoints
    def add_endpoint(self, node: Node):
        assert len(self._endpoints) < self._num_topological
        self._endpoints.append(node)
        super().add_node(node)

    def get_endpoints(self) -> tp.List[SubNode]:
        return self._endpoints

    # parameter
    def add_parameter(self, node: ParameterNode):
        self._parameters.append(node)
        super().add_node(node)

    def has_parameters(self) -> bool:
        return len(self._parameters) > 0

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return self._parameters

    # information
    def add_info_node(self, node: SubInformationNode):
        assert self.get_dim() == node.get_dim()
        self.set_info_matrix(SquareFactory.from_dim(self.get_dim()).identity())
        self._info_node = node
        super().add_node(node)

    def has_info_node(self) -> bool:
        return self._info_node is not None

    def get_info_node(self) -> SubInformationNode:
        assert self.has_info_node(), 'No information-node is present.'
        return self._info_node

    # read/write
    def read(self, words: tp.List[str]) -> tp.List[str]:
        words = self.get_data().read_rest(words)
        if not self.has_info_node():
            words = self._info_matrix.read_rest(words)
        return words

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self.get_data().write()
        if not self.has_info_node():
            words += self._info_matrix.write()
        return words
