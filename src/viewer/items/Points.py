from typing import *
from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.structures import *
from src.viewer.items.Drawer import Drawer
from src.viewer.colours import *


class Points(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, points: List[Vector], width: float = 4, colour: Optional[Colour] = Colours.WHITE):
        super().__init__()
        self._points: List[Vector] = points
        # settings
        self._width: float = width
        self._colour: Colour = colour

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
            type(self).point(point, self._colour)

        glEnd()
        glDisable(GL_POINT_SMOOTH)
        glBlendFunc(GL_NONE, GL_NONE)
        glDisable(GL_BLEND)
