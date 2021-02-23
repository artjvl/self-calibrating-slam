from typing import *

from OpenGL.GL import *

from src.framework.graph.factor import FactorElement, FactorEdge
from src.framework.structures import *
from src.gui.viewer.Colour import Colour
from src.gui.viewer.Drawer import Drawer
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Edges(GraphicsItem):

    name = 'Constraint edges'

    # constructor
    def __init__(
            self,
            pairs: List[Tuple[Vector, Vector]],
            colour: Optional[Tuple[float, ...]] = Colour.WHITE,
            width: float = 2,
            gl_options: str = 'translucent'
    ):
        super().__init__(colour)
        self._pairs: List[Tuple[Vector, Vector]] = pairs
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

        for pair in self._pairs:
            Drawer.line(*pair, colour=self._colour)

        glEnd()

    # eligibility method
    @staticmethod
    def check(element: Type[Any]) -> bool:
        if issubclass(element, FactorEdge) and element.is_physical:
            return True
        return False

    # constructor method
    @classmethod
    def from_elements(cls, elements: List[Any]) -> GraphicsItem:
        element_type = type(elements[0])
        return cls(
            [edge.get_endpoints3() for edge in elements],
            colour=Colour.similar(element_type.colour)
        )
