from __future__ import annotations

import typing as tp

from OpenGL.GL import *
from src.framework.graph.Visualisable import DrawEdge
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Drawer import Drawer
from src.gui.viewer.Rgb import Rgb, RgbTuple
from src.gui.viewer.items.GraphicsItem import GraphicsItem

if tp.TYPE_CHECKING:
    from src.framework.graph.Visualisable import SubVisualisable

Nodeset = tp.Tuple[Vector3, Vector3]


class Edges(GraphicsItem):

    name = 'Constraint edges'

    # constructor
    def __init__(
            self,
            nodesets: tp.List[Nodeset],
            colour: tp.Optional[RgbTuple] = Rgb.WHITE,
            width: float = 2,
            gl_options: str = 'translucent'
    ):
        super().__init__(colour)
        self._nodesets: tp.List[Nodeset] = nodesets
        # settings
        self._width: float = width
        self.setGLOptions(gl_options)

    # public method
    def paint(self):
        self.setupGLState()

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)  #
        glDepthMask(False)  #

        glLineWidth(self._width)
        glBegin(GL_LINES)

        for nodeset in self._nodesets:
            Drawer.line(*nodeset, colour=self._colour)

        glEnd()

    # constructor method
    @staticmethod
    def check(element_type: tp.Type['SubVisualisable']) -> bool:
        return issubclass(element_type, DrawEdge)

    @classmethod
    def from_elements(cls, elements: tp.List[DrawEdge]) -> Edges:
        poses: tp.List[Nodeset] = [element.draw_nodeset() for element in elements]
        return cls(
            poses,
            colour=Rgb.similar(DrawEdge.draw_rgb())
        )
