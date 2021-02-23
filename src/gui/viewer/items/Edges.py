from typing import *

from OpenGL.GL import *

from src.framework.graph.factor import FactorElement, FactorEdge
from src.framework.structures import *
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Edges(GraphicsItem):

    name = 'Constraint edges'

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

    # eligibility method
    @staticmethod
    def check(element: Type[FactorElement]) -> bool:
        if issubclass(element, FactorEdge) and element.is_physical:
            return True
        return False

    # constructor method
    @classmethod
    def from_elements(cls, elements: List[FactorElement]) -> GraphicsItem:
        return cls([edge.get_endpoints3() for edge in elements])
