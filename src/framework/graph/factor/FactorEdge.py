from abc import ABC, abstractmethod
from typing import *

from src.framework.graph.base import *
from src.framework.graph.factor.FactorElement import FactorElement
from src.framework.graph.factor.FactorNode import FactorNode
from src.framework.structures import *

T = TypeVar('T')


class FactorEdge(Generic[T], BaseEdge, FactorElement[T], ABC):

    # constructor
    def __init__(self, nodes: List[FactorNode], value: T, information: Optional[Square] = None):
        super().__init__(nodes=nodes, value=value)
        if information is None:
            self._is_uncertain = False
        else:
            self._is_uncertain = True
        self._information = information

    # public methods
    def is_uncertain(self) -> bool:
        return self._is_uncertain

    def get_information(self) -> Square:
        return self._information

    def set_information(self, information: Square):
        self._information = information
        self._is_uncertain = True

    @abstractmethod
    def compute_error(self) -> float:
        pass

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def size(cls):
        pass

    # abstract methods
    @classmethod
    @abstractmethod
    def from_nodes(cls, nodes):
        pass
