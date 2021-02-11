from abc import ABC
from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.base import *
from src.framework.graph.factor.FactorElement import FactorElement


class FactorNode(BaseNode, FactorElement, ABC):

    # constructor
    def __init__(self, id: int, value: Union[Vector, SO, SE]):
        super().__init__(id=id, value=value)
