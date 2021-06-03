import typing as tp
from abc import ABC, abstractmethod

from src.framework.graph.BaseGraph import SubBaseNode
from src.framework.graph.FactorGraph import FactorEdge, SubFactorNode, FactorNode
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode, SubInformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode, SubParameterNode

SubCalibratingEdge = tp.TypeVar('SubCalibratingEdge', bound='CalibratingEdge')
T = tp.TypeVar('T')


class CalibratingEdge(tp.Generic[T], FactorEdge[T], ABC):

    _num_endpoints: int

    def __init__(
            self,
            *nodes: SubFactorNode
    ):
        assert len(nodes) in (0, self._num_endpoints)

        self._num_additional: int = 0
        self._endpoints: tp.List[SubFactorNode] = []
        self._parameters: tp.List[SubParameterNode] = []
        self._info_node: tp.Optional[SubInformationNode] = None
        super().__init__(*nodes)

    # attributes
    def get_cardinality(self) -> int:
        return self._num_endpoints + self._num_additional

    def set_num_additional(self, num_additional: int) -> None:
        """ Sets the number of additional (beyond the number of topological) nodes. """
        self._num_additional = num_additional

    @abstractmethod
    def get_value(self) -> T:
        """ Returns a (topological) measure (i.e., 'value') inferred by the connected (topological) nodes. """
        pass

    # override
    def add_node(self, node: SubBaseNode) -> None:
        assert isinstance(node, FactorNode)

        if isinstance(node, ParameterNode):
            self.add_parameter(node)
        elif isinstance(node, InformationNode):
            self.add_info_node(node)
        else:
            self.add_endpoint(node)

    # endpoints
    def add_endpoint(self, node: FactorNode):
        self._endpoints.append(node)
        super().add_node(node)

    def get_endpoints(self) -> tp.List[SubFactorNode]:
        return self._endpoints

    # parameter
    def add_parameter(self, node: ParameterNode):
        self._parameters.append(node)
        super().add_node(node)

    def has_parameters(self) -> bool:
        return len(self._parameters) != 0

    def get_parameters(self) -> tp.List[SubParameterNode]:
        return self._parameters

    # information
    def add_info_node(self, node: SubInformationNode):
        assert self.get_dim() == node.get_dimension()
        self._info_node = node
        super().add_node(node)

    def has_info_node(self) -> bool:
        return self._info_node is not None

    def get_info_node(self) -> SubInformationNode:
        assert self.has_info_node(), 'No information-node is present.'
        return self._info_node

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._measurement.read_rest(words)
        if not self.has_info_node():
            words = self._info_matrix.read_rest(words)
        assert not words, f"Words '{words}' are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._measurement.write()
        if not self.has_info_node():
            words += self._info_matrix.write()
        return words

    # ReadWrite: @classmethod
    def get_length(self) -> int:
        return self._measurement.get_length() + (self._info_node.get_length() if self.has_info_node() else 0)
