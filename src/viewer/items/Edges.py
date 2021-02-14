from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.groups import *
from src.framework.graph import *
from src.viewer.items.Drawer import Drawer


class Edges(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, graph: Graph, width: float = 3, anti_alias: bool = True, gl_options: str = 'translucent'):
        super().__init__()
        self.setGLOptions(gl_options)
        self._anti_alias = anti_alias
        self._width = width
        self._vertices = []
        for edge in graph.get_edges():
            connected_set = [node.get_point3() for node in edge.get_nodes()]
            self._vertices.append(tuple(connected_set))

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
