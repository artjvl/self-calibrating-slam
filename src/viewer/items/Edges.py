from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.graph import *
from src.viewer.items.Drawer import Drawer


class Edges(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, graph: Graph, width: float = 2, anti_alias: bool = True, gl_options: str = 'translucent'):
        super().__init__()
        self.setGLOptions(gl_options)
        self._anti_alias = anti_alias
        self._width = width
        self._vertices = []
        for edge in graph.get_edges():
            nodes = edge.get_nodes()
            self._vertices.append((nodes[0].get_value().to_se3().translation(),
                                   nodes[1].get_value().to_se3().translation()))

    # public method
    def paint(self):
        self.setupGLState()

        if self._anti_alias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self._width)

        glBegin(GL_LINES)

        for pair in self._vertices:
            self.line(*pair)

        glEnd()
