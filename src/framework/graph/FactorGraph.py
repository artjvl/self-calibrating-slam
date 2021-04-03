import typing as tp
from abc import abstractmethod

from src.framework.graph.BaseGraph import BaseGraph, BaseNode, BaseEdge
from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.protocols.ReadWrite import ReadWrite
from src.framework.structures import Vector, Square

Node = tp.TypeVar('Node', bound='FactorNode')
Edge = tp.TypeVar('Edge', bound='FactorEdge')
Element = tp.Union[Node, Edge]

SubVector = tp.TypeVar('SubVector', bound=Vector)
SubSquare = tp.TypeVar('SubSquare', bound=Square)


class FactorGraph(BaseGraph[Node, Edge]):

    # error
    def compute_error(self) -> float:
        error: float = 0
        for edge in self.get_edges():
            error += edge.compute_error()
        return error


class FactorNode(BaseNode, ReadWrite):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__(id_)
        self._is_fixed = False

    def fix(self, is_fixed: bool = True) -> None:
        self._is_fixed = is_fixed

    def is_fixed(self) -> bool:
        return self._is_fixed

    # value
    @abstractmethod
    def get_value(self) -> Supported:
        pass


class FactorEdge(BaseEdge[Node], ReadWrite):

    def __init__(
            self,
            nodes: tp.Optional[tp.List[Node]] = None
    ):
        super().__init__(nodes)
        self._cardinality: int = 0

    # cardinality
    def get_cardinality(self) -> int:
        return self._cardinality

    # measurement
    @abstractmethod
    def get_measurement(self) -> Supported:
        pass

    # estimate
    @abstractmethod
    def get_estimate(self) -> Supported:
        pass

    # information
    @abstractmethod
    def is_uncertain(self) -> bool:
        pass

    @abstractmethod
    def get_information(self) -> SubSquare:
        pass

    # error
    @abstractmethod
    def compute_error_vector(self) -> SubVector:
        pass

    def compute_error(self) -> float:
        error_vector: SubVector = self.compute_error_vector()
        return self.mahalanobis_distance(error_vector, self.get_information())

    # helper methods
    @staticmethod
    def mahalanobis_distance(
            vector: SubVector,
            information: SubSquare
    ) -> float:
        assert vector.get_dimension() == information.get_dimension(), f'{vector} and {information} are not of appropriate dimensions.'
        return vector.transpose() * information * vector
