from abc import ABC, abstractmethod
from typing import *

from src.framework.graph.base.BaseNode import BaseNode
from src.framework.graph.factor.FactorElement import FactorElement
from src.framework.groups import SO3, SE3
from src.framework.groups.Group import Group
from src.framework.structures import Vector

T = TypeVar('T', bound=Union[Vector, Group])


class FactorNode(BaseNode, FactorElement[T], ABC):

    # constructor
    def __init__(self, id: int, value: T):
        super().__init__(id=id, value=value)
        self._is_fixed = False

    # static properties
    @property
    @classmethod
    @abstractmethod
    def has_rotation(cls) -> bool:
        pass

    # 3-dimensional getters
    @abstractmethod
    def get_translation3(self) -> Vector:
        pass

    @abstractmethod
    def get_rotation3(self) -> SO3:
        pass

    @abstractmethod
    def get_pose3(self) -> SE3:
        pass

    # public method
    def set_fixed(self):
        self._is_fixed = True
