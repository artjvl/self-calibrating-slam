from abc import ABC, abstractmethod
from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.base import *
from src.framework.graph.factor.FactorElement import FactorElement


class FactorNode(BaseNode, FactorElement, ABC):

    # constructor
    def __init__(self, id: int, value: Union[Vector, SO, SE]):
        super().__init__(id=id, value=value)

    # abstract methods
    @abstractmethod
    def get_point3(self) -> Vector:
        pass

    @property
    @classmethod
    @abstractmethod
    def has_rotation(cls) -> bool:
        pass

    @abstractmethod
    def get_rotation3(self) -> SO3:
        pass
