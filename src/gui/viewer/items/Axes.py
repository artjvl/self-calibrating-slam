from typing import *

from OpenGL.GL import *

from src.framework.graph.factor import FactorNode, FactorEdge
from src.framework.groups import *
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Axes(GraphicsItem):

    name = 'Axis systems'

    # constructor
    def __init__(self, poses: List[SE3], width: float = 3, size: float = 0.2, gl_options: str = 'translucent'):
        super().__init__()
        self._poses: List[SE3] = poses
        # settings
        self.setGLOptions(gl_options)
        self._width: float = width
        self._size: float = size

    # public method
    def paint(self):
        self.setupGLState()

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glLineWidth(self._width)
        glBegin(GL_LINES)

        for pose in self._poses:
            type(self).axis(pose, self._size)

        glEnd()

    # eligibility method
    @staticmethod
    def check(element: Any) -> bool:
        if issubclass(element, FactorNode) and element.is_physical and element.has_rotation:
            return True
        return False

    # constructor method
    @classmethod
    def from_elements(cls, elements: Union[List[FactorNode], List[FactorEdge]]) -> GraphicsItem:
        return cls([node.get_pose3() for node in elements])
