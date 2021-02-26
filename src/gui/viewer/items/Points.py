from typing import *

from OpenGL.GL import *

from src.framework.graph.factor.FactorNode import FactorNode
from src.framework.structures import *
from src.gui.viewer.Colour import Colour
from src.gui.viewer.Drawer import Drawer
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Points(GraphicsItem):

    name = 'Node points'

    # constructor
    def __init__(
            self,
            points: List[Vector],
            colour: Optional[Tuple[float, ...]] = Colour.WHITE,
            width: float = 4
    ):
        super().__init__(colour)
        self._points: List[Vector] = points
        # settings
        self._width: float = width

    # public method
    def paint(self):
        # reference: https://stackoverflow.com/questions/17274820/drawing-round-points-using-modern-opengl

        self.setupGLState()

        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_NOTEQUAL, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(self._width)

        glBegin(GL_POINTS)

        for point in self._points:
            Drawer.point(point, colour=self._colour)

        glEnd()
        glDisable(GL_POINT_SMOOTH)
        glBlendFunc(GL_NONE, GL_NONE)
        glDisable(GL_BLEND)

    # eligibility method
    @staticmethod
    def check(element_type: Type[Any]) -> bool:
        if issubclass(element_type, FactorNode) and element_type.is_physical:
            return True
        return False

    # constructor method
    @classmethod
    def from_elements(cls, elements: List[Any]) -> GraphicsItem:
        element_type = type(elements[0])
        return cls(
            [node.get_translation3() for node in elements],
            colour=Colour.similar(element_type.colour)
        )
