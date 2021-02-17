from typing import *
from OpenGL.GL import *
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem

from src.framework.groups import *
from src.viewer.items.Drawer import Drawer


class Axes(GLGraphicsItem, Drawer):

    # constructor
    def __init__(self, poses: List[SE3], width: float = 3, size: float = 0.2, anti_alias: bool = True, gl_options: str = 'translucent'):
        super().__init__()
        self._poses: List[SE3] = poses
        # settings
        self.setGLOptions(gl_options)
        self._anti_alias: bool = anti_alias
        self._width: float = width
        self._size: float = size

    # public method
    def paint(self):
        self.setupGLState()

        if self._anti_alias:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self._width)
        glBegin(GL_LINES)

        for pose in self._poses:
            type(self).axis(pose, self._size)

        glEnd()
