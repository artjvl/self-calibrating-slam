from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.graph import *
from src.viewer.items.Drawer import Drawer


class Edges(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, graph, width=2, anti_alias=True, gl_options='translucent'):
        assert isinstance(graph, Graph)
        super().__init__()
        self.setGLOptions(gl_options)
        self._anti_alias = anti_alias
        self._width = width
        self._graph = graph

    # public method
    def paint(self):
        self.setupGLState()

        if self._anti_alias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self._width)

        glBegin(GL_LINES)

        for edge in self._graph.get_edges():
            a = edge.get_nodes()[0]
            b = edge.get_nodes()[1]
            self.line(a.get_value().to_se3().translation(),
                      b.get_value().to_se3().translation())

        glEnd()
