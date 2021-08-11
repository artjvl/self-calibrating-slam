from __future__ import annotations

import typing as tp

from OpenGL.GL import *

from src.framework.graph.protocols.Visualisable import Visualisable, DrawAxis
from src.framework.math.lie.transformation import SE3
from src.gui.viewer.Drawer import Drawer
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Axes(GraphicsItem):

    name = 'Axis systems'

    # constructor
    def __init__(
            self,
            poses: tp.List[SE3],
            width: float = 3,
            size: float = 0.2,
            gl_options: str = 'translucent'
    ):
        super().__init__()
        self._poses: tp.List[SE3] = poses
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
            Drawer.axis(pose, self._size)

        glEnd()

    # constructor method
    @staticmethod
    def check(element_type: tp.Type[Visualisable]) -> bool:
        return issubclass(element_type, DrawAxis)

    @classmethod
    def from_elements(cls, elements: tp.List[DrawAxis]) -> Axes:
        poses: tp.List[SE3] = [element.draw_pose() for element in elements]
        return cls(poses)
