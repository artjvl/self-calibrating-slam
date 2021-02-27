from __future__ import annotations

from abc import ABC, abstractmethod
from typing import *

from src.framework.graph.base.BaseEdge import BaseEdge
from src.framework.graph.factor.FactorElement import FactorElement
from src.framework.graph.factor.FactorNode import FactorNode
from src.framework.groups.Group import Group
from src.framework.structures import Vector, Square

T = TypeVar('T', bound=Union[Vector, Group])


class FactorEdge(BaseEdge, FactorElement[T], ABC):

    # constructor
    def __init__(
            self,
            nodes: List[FactorNode],
            value: T,
            information: Optional[Square] = None
    ):
        super().__init__(nodes=nodes, value=value)
        self._information: Optional[Square] = information
        self._is_uncertain: bool = True
        if information is None:
            self._is_uncertain = False

    # getters/setters
    def is_uncertain(self) -> bool:
        return self._is_uncertain

    def get_information(self) -> Square:
        assert self._information is not None
        return self._information

    def set_information(self, information: Square):
        self._information = information
        self._is_uncertain = True

    # abstract properties
    @property
    @classmethod
    @abstractmethod
    def cardinality(cls) -> int:
        pass

    # error methods
    @abstractmethod
    def compute_error_vector(self) -> Vector:
        pass

    @abstractmethod
    def compute_error(self) -> float:
        pass

    # alternative constructor
    @classmethod
    @abstractmethod
    def from_nodes(cls, nodes) -> FactorEdge:
        pass

    # 3-dimensional getter
    @abstractmethod
    def get_endpoints3(self) -> Tuple[Vector, Vector]:
        pass
