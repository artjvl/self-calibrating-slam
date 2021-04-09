import typing as tp
from abc import ABC, abstractmethod

from src.framework.graph.BaseGraph import Node
from src.framework.graph.FactorGraph import FactorEdge
from src.framework.graph.data import SubData, SubDataSquare
from src.framework.graph.data.DataFactory import DataFactory
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode, SubCalibratingNode
from src.framework.graph.types.scslam2d.nodes.information.InformationNode import InformationNode, SubInformationNode
from src.framework.graph.types.scslam2d.nodes.parameter.ParameterNode import ParameterNode, SubParameterNode
from src.framework.math.matrix.square import SubSquare, SquareFactory

SubCalibratingEdge = tp.TypeVar('SubCalibratingEdge', bound='CalibratingEdge')
T = tp.TypeVar('T')


class CalibratingEdge(tp.Generic[T], FactorEdge[T], ABC):
    _type: tp.Type[T]
    _num_endpoints: int

    def __init__(
            self,
            *nodes: SubCalibratingNode
    ):
        assert len(nodes) in (0, self._num_endpoints)
        super().__init__(*nodes)

        self._num_additional: int = 0

        self._measurement: SubData = DataFactory.from_type(self.get_type())()
        self._info_matrix: SubDataSquare = DataFactory.from_value(
            SquareFactory.from_dim(self.get_dimension()).identity()
        )

        self._endpoints: tp.List[SubCalibratingNode] = []
        self._parameters: tp.List[SubParameterNode] = []
        self._information: tp.Optional[SubInformationNode] = None

    # attributes
    def get_cardinality(self) -> int:
        return self._num_endpoints + self._num_additional

    def set_num_additional(self, num_additional: int) -> None:
        self._num_additional = num_additional

    @abstractmethod
    def get_value(self) -> T:
        pass

    # measurement
    def set_measurement(self, measurement: T) -> None:
        self._measurement.set_value(measurement)

    def get_measurement(self) -> T:
        assert self._measurement.has_value()
        return self._measurement.get_value()

    @classmethod
    def get_type(cls) -> tp.Type[T]:
        return cls._type

    @classmethod
    def get_dimension(cls) -> int:
        return DataFactory.from_type(cls.get_type()).get_length()

    # (information) matrix
    def set_information(self, matrix: SubSquare) -> None:
        self._info_matrix.set_value(matrix)

    def get_information(self) -> SubSquare:
        assert self._info_matrix.has_value()
        return self._info_matrix.get_value()

    # override
    def add_node(self, node: Node) -> None:
        assert isinstance(node, CalibratingNode)

        if isinstance(node, ParameterNode):
            self.add_parameter(node)
        elif isinstance(node, InformationNode):
            self.add_info_node(node)
        else:
            self.add_endpoint(node)

    # endpoints
    def add_endpoint(self, node: CalibratingNode):
        self._endpoints.append(node)
        super().add_node(node)

    def get_endpoints(self) -> tp.List[SubCalibratingNode]:
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
        assert self.get_dimension() == node.get_dimension()
        self._information = node
        super().add_node(node)

    def has_info_node(self) -> bool:
        return self._information is not None

    def get_info_node(self) -> SubInformationNode:
        assert self.has_info_node(), 'No information-node is present.'
        return self._information

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._measurement.read_rest(words)
        if not self.has_info_node():
            words = self._info_matrix.read_rest(words)
        assert not words, f"Words '{words}' are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._measurement.write()
        if not self.has_info_node():
            words += self._information.write()
        return words

    # ReadWrite: @classmethod
    def get_length(self) -> int:
        return self._measurement.get_length() + (self._information.get_length() if self.has_info_node() else 0)
