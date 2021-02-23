from typing import *
import numpy as np

from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.structures import Vector
from src.gui.viewer.Colour import Colour
from src.gui.viewer.Drawer import Drawer


class Grid(GLGraphicsItem):

    name = 'Constraint edges'

    # constructor
    def __init__(
            self,
            size: Tuple[float, float] = (100., 100.),
            spacing: Tuple[float, float] = (1., 1.),
            gl_options: str = 'translucent'
    ):
        super().__init__()
        assert all((0.5 * dim).is_integer() for dim in size)
        self._size: Tuple[float, float] = (0.5 * size[0], 0.5 * size[1])
        self._spacing: Tuple[float, float] = spacing
        # settings
        self.setGLOptions(gl_options)

    # public method
    def paint(self):
        self.setupGLState()
        alpha = 0.2

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)  #
        glDepthMask(False)  #

        glBegin(GL_LINES)

        size_x, size_y = self._size
        delta_x, delta_y = self._spacing
        steps_x: np.ndarray = np.arange(0, size_x + 0.001, delta_x)
        steps_y: np.ndarray = np.arange(0, size_y + 0.001, delta_y)
        for x in steps_x[1:]:
            a = Vector([x, size_y, 0])
            b = Vector([x, -size_y, 0])
            Drawer.line(a, b, colour=Colour.WHITE, alpha=alpha)
            a = Vector([-x, size_y, 0])
            b = Vector([-x, -size_y, 0])
            Drawer.line(a, b, colour=Colour.WHITE, alpha=alpha)
        for y in steps_y[1:]:
            a = Vector([size_x, y, 0])
            b = Vector([-size_x, y, 0])
            Drawer.line(a, b, colour=Colour.WHITE, alpha=alpha)
            a = Vector([size_x, -y, 0])
            b = Vector([-size_x, -y, 0])
            Drawer.line(a, b, colour=Colour.WHITE, alpha=alpha)
        a = Vector([size_x, 0, 0])
        b = Vector([-size_x, 0, 0])
        Drawer.line(a, b, colour=Colour.RED, alpha=alpha * 2)
        a = Vector([0, size_y, 0])
        b = Vector([0, -size_y, 0])
        Drawer.line(a, b, colour=Colour.GREEN, alpha=alpha * 2)
        a = Vector([0, 0, size_x])
        b = Vector([0, 0, -size_x])
        Drawer.line(a, b, colour=Colour.BLUE, alpha=alpha * 2)

        glEnd()
