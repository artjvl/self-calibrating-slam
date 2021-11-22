from __future__ import annotations

import typing as tp

from OpenGL.GL import *
from src.framework.graph.Visualisable import SubVisualisable, DrawPoint
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Drawer import Drawer
from src.gui.viewer.Rgb import Rgb, RgbTuple
from src.gui.viewer.items.GraphicsItem import GraphicsItem

if tp.TYPE_CHECKING:
    from src.framework.graph.Visualisable import SubVisualisable


class Points(GraphicsItem):
    name = 'Node points'

    # constructor
    def __init__(
            self,
            points: tp.List[Vector3],
            colour: tp.Optional[RgbTuple] = Rgb.WHITE,
            width: float = 4
    ):
        super().__init__(colour)
        self._points: tp.List[Vector3] = points
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

    # constructor method
    @staticmethod
    def check(element_type: tp.Type['SubVisualisable']) -> bool:
        return issubclass(element_type, DrawPoint)

    @classmethod
    def from_elements(cls, elements: tp.List[DrawPoint]) -> Points:
        poses: tp.List[Vector3] = [element.draw_point() for element in elements]
        return cls(
            poses,
            colour=Rgb.similar(DrawPoint.draw_rgb())
        )
