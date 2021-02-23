from __future__ import annotations

from abc import ABC, abstractmethod
from typing import *

from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.gui.viewer.Colour import Colour


class MetaGraphicsItem(type(ABC), type(GLGraphicsItem)):
    pass


class GraphicsItem(ABC, GLGraphicsItem, metaclass=MetaGraphicsItem):

    # constructor
    def __init__(self, colour: Optional[Tuple[float, ...]] = None):
        super().__init__()
        if colour is None:
            colour = Colour.WHITE
        self._colour: Tuple[float, ...] = colour

    def set_colour(self, colour: Tuple[float, ...]):
        self._colour = colour

    def get_colour(self) -> Tuple[float, ...]:
        return self._colour

    # static properties
    @property
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    # eligibility method
    @staticmethod
    @abstractmethod
    def check(element: Any) -> bool:
        pass

    # constructor method
    @classmethod
    @abstractmethod
    def from_elements(cls, elements: List[Any]) -> GraphicsItem:
        pass
