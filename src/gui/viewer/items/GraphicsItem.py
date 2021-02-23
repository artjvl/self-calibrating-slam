from __future__ import annotations

from abc import ABC, abstractmethod
from typing import *

from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.graph.factor import FactorElement
from src.framework.groups import *
from src.framework.structures import *
from src.gui.viewer.Colour import Colour


class MetaGraphicsItem(type(ABC), type(GLGraphicsItem)):
    pass


class GraphicsItem(ABC, GLGraphicsItem, metaclass=MetaGraphicsItem):

    # constructor
    def __init__(self):
        super().__init__()

    # static properties
    @property
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        pass

    # utility-methods
    @staticmethod
    def axis(pose: SE3, size: Optional[float] = 0.2):
        centre = pose.translation()
        matrix = pose.rotation().matrix()
        units = [Vector([1, 0, 0]),
                 Vector([0, 1, 0]),
                 Vector([0, 0, 1])]
        x = size * Vector(matrix @ units[0])
        y = size * Vector(matrix @ units[1])
        z = size * Vector(matrix @ units[2])

        alpha = .6

        glColor4f(1, 0, 0, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + x))

        glColor4f(0, 1, 0, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + y))

        glColor4f(0, 0, 1, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + z))

    @staticmethod
    def line(a: Vector, b: Vector, colour: Optional[Colour] = Colour.WHITE):
        glColor4f(*colour, 0.5)
        glVertex3f(*(a.to_list()))
        glVertex3f(*(b.to_list()))

    @staticmethod
    def point(point: Vector, colour: Optional[Colour] = Colour.WHITE):
        glColor4f(*colour, 0.5)
        glVertex3f(*(point.to_list()))

    # eligibility method
    @staticmethod
    @abstractmethod
    def check(element: FactorElement) -> bool:
        pass

    # constructor method
    @classmethod
    @abstractmethod
    def from_elements(cls, elements: List[FactorElement]) -> GraphicsItem:
        pass
