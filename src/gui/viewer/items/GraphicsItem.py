import typing as tp
from abc import abstractmethod

from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from src.gui.viewer.Rgb import Rgb, RgbTuple

if tp.TYPE_CHECKING:
    from src.framework.graph.Visualisable import SubVisualisable

SubGraphicsItem = tp.TypeVar('SubGraphicsItem', bound='GraphicsItem')


class GraphicsItem(GLGraphicsItem):
    name: str

    # constructor
    def __init__(self, colour: tp.Optional[RgbTuple] = Rgb.WHITE):
        super().__init__()
        self._colour: RgbTuple = colour

    def set_colour(self, colour: RgbTuple) -> None:
        self._colour = colour

    def get_colour(self) -> RgbTuple:
        return self._colour

    # eligibility method
    @staticmethod
    @abstractmethod
    def check(element_type: tp.Type['SubVisualisable']) -> bool:
        pass

    # constructor method
    @classmethod
    @abstractmethod
    def from_elements(cls, elements: tp.List['SubVisualisable']) -> SubGraphicsItem:
        pass
