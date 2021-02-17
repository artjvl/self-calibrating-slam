from typing import *
from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.structures import *
from src.viewer.items.Drawer import Drawer


class Edges(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, pairs: List[Tuple[Vector, Vector]], width: float = 1, gl_options: str = 'translucent'):
        super().__init__()
        self._pairs: List[Tuple[Vector, Vector]] = pairs
        # settings
        self.setGLOptions(gl_options)
        self._width: float = width

    # public method
    def paint(self):
        self.setupGLState()

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)  #
        glDepthMask(False)  #

        glLineWidth(self._width)
        glBegin(GL_LINES)

        for pair in self._pairs:
            self.line(*pair)

        glEnd()
