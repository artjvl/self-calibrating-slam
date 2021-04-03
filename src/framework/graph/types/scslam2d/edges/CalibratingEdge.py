import typing as tp
from abc import ABC, abstractmethod

from src.framework.graph.FactorGraph import FactorEdge, SubSquare
from src.framework.graph.attributes.DataFactory import DataSquare, Supported
from src.framework.graph.protocols.ContainsData import ContainsData
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import SubNode
from src.framework.graph.types.scslam2d.nodes.InformationNode import SubInfoNode, InformationNode
from src.framework.graph.types.scslam2d.nodes.ParameterNode import SubParamNode, ParameterNode
from src.framework.structures import Square


class CalibratingEdge(FactorEdge, ContainsData, ABC):

    # number of endpoints
    endpoints: int

    # default node data-types (parameter / information)
    default_paramtype: tp.Optional[tp.Type[Supported]] = None
    default_infotype: tp.Optional[tp.Type[Supported]] = None

    def __init__(
            self,
            nodes: tp.Optional[tp.List[SubNode]] = None
    ):
        super().__init__(nodes)
        self._cardinality = self.endpoints + int(self.default_paramtype is not None) + int(self.default_infotype is not None)

        self._paramtype: tp.Optional[tp.Type[Supported]] = self.default_paramtype
        self._infotype: tp.Optional[tp.Type[Supported]] = self.default_paramtype

        # info
        self._info = DataSquare(Square.identity(3))

    # param
    def has_default_paramtype(self) -> bool:
        """ Returns whether a default type is defined for the parameter. """
        return self.default_paramtype is not None

    def set_paramtype(self, type_: tp.Type[Supported]) -> None:
        """ Sets the parameter type. """
        assert not self.has_default_paramtype(), f'Default parameter-type {self.default_paramtype} cannot be overwritten.'
        self._paramtype = type_
        self._cardinality += 1

    def get_paramtype(self) -> tp.Type[Supported]:
        """ Returns the parameter type. """
        assert self._paramtype is not None
        return self._paramtype

    def set_paramnode(self, node: SubParamNode) -> None:
        """ Configures the parameter by adding its node and storing its type. """
        type_: tp.Type[Supported] = node.get_datatype()
        self.set_paramtype(type_)
        self.add_node(node)

    # info
    def has_default_infotype(self) -> bool:
        """ Returns whether a default encoding for the (external) information matrix is defined. """
        return self.default_infotype is not None

    def set_infotype(self, type_: tp.Type[Supported]) -> None:
        """ Sets the encoding type of the (external) information matrix. """
        assert not self.has_default_infotype(), f'Default parameter-type {self.default_infotype} cannot be overwritten.'
        self._infotype = type_
        self._cardinality += 1

    def get_infotype(self) -> tp.Type[Supported]:
        """ Returns the encoding type of the (external) information matrix. """
        assert self._infotype is not None
        return self._infotype

    def set_infonode(self, node: SubInfoNode) -> None:
        """ Configures the (external) information matrix by adding its node and storing its type. """
        type_: tp.Type[Supported] = node.get_datatype()
        self.set_infotype(type_)
        self.add_node(node)

    # node addition
    def add_node(self, node: SubNode) -> None:
        """ Adds a node to the edge. """
        size: int = len(self.get_nodes())
        assert size < self._cardinality, f'Number of nodes {size} has already reached its allowed cardinality {self._cardinality}.'
        if isinstance(node, ParameterNode):
            assert self._paramtype is not None, f'No parameter-type is defined for the added ParameterNode.'
            assert node.get_datatype() is self._paramtype, f'Parameter node-type {node.get_datatype()} should be {self._paramtype}.'
        elif isinstance(node, InformationNode):
            assert self._infotype is not None, f'No information-type is defined for the added InformationNode.'
            assert node.get_datatype() is self._infotype, f'Information SubNode-type {node.get_datatype()} should be {self._infotype}.'
        super().add_node(node)

    # checks
    def is_uncertain(self) -> bool:
        """ Returns whether the edge is uncertain (i.e., whether an information matrix is defined). """
        return True

    # nodes
    def get_paramnode(self) -> SubParamNode:
        """ Returns the node that encodes the calibration parameter. """
        assert self._paramtype is not None
        for node in self.get_nodes():
            if isinstance(node, ParameterNode):
                return node
        # return self.get_node(self.endpoints)

    def get_infonode(self) -> SubInfoNode:
        """ Returns the node that encodes the (external) information matrix. """
        assert self._infotype is not None
        for node in self.get_nodes():
            if isinstance(node, InformationNode):
                return node
        # return self.get_node(self.get_cardinality() - 2)

    # data access
    @abstractmethod
    def get_value(self) -> Supported:
        """ Returns the 'value' of the edge as defined by its physical nodes (i.e., poses and points). """
        pass

    @abstractmethod
    def get_estimate(self) -> Supported:
        """ Returns the estimate of the edge measurement as defined by all its nodes (including parameters). """
        pass

    def set_measurement(self, measurement: Supported) -> None:
        """ Assigns the measurement value to the edge. """
        self.set_data(measurement)

    def get_measurement(self) -> Supported:
        """ Returns the measurement value assigned to the edge. """
        return self.get_data()

    def set_information(self, information: SubSquare) -> None:
        """ Sets the (internal) information matrix of the edge. """
        self._info.set_value(information)

    def get_information(self) -> SubSquare:
        """ Returns the information matrix that describes the accuracy of the measurement. """
        if self._infotype is None:
            return self._info.get_value()
        return self.get_infonode().get_value()

    # read/write
    def read(self, words: tp.List[str]):
        """ Reads a list of strings and stores the corresponding data. """
        words = self._data.read_rest(words)
        if self._infotype is None:
            words = self._info.read_rest(words)
        assert not words, f"Words '{words}' are left unread."

    def write(self) -> tp.List[str]:
        """ Writes its internally stored data to a list of words. """
        words: tp.List[str] = self._data.write()
        if self._infotype is None:
            words += self._info.write()
        return words

    def get_word_count(self) -> int:
        return 0
