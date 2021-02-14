from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.groups import *
from src.framework.graph import *
from src.viewer.items.Drawer import Drawer


class Axes(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, graph: Graph, width: float = 3, size: float = 0.2, anti_alias: bool = True, gl_options: str = 'translucent'):
        super().__init__()
        self.setGLOptions(gl_options)
        self._anti_alias = anti_alias
        self._poses = []
        for node in graph.get_nodes():
            if node.has_rotation:
                pose = node.get_value()
                if isinstance(pose, SE2):
                    pose = pose.to_se3()
                self._poses.append(pose)
        # self._poses = [pose.get_value().to_se3() for pose in graph.get_nodes()]
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
