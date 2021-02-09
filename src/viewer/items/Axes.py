from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.graph import *
from src.viewer.items.Drawer import Drawer


class Axes(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, graph: Graph, width: float = 3, size: float = 0.2, anti_alias: bool = True, gl_options: str = 'translucent'):
        super().__init__()
        self.setGLOptions(gl_options)
        self._anti_alias = anti_alias
        self._poses = [pose.get_value().to_se3() for pose in graph.get_nodes()]
        self._width = width
        self._size = size

    # public method
    def paint(self):
        self.setupGLState()

        if self._anti_alias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self._width)

        glBegin(GL_LINES)

        for pose in self._poses:
            self.axis(pose, self._size)

        glEnd()
