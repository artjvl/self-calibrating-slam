from enum import Enum
from typing import Type

from src.gui.viewer.items.Axes import Axes
from src.gui.viewer.items.Edges import Edges
from src.gui.viewer.items.GraphicsItem import GraphicsItem
from src.gui.viewer.items.Points import Points


class Items(Enum):
    POINTS: Type[GraphicsItem] = Points
    EDGES: Type[GraphicsItem] = Edges
    AXES: Type[GraphicsItem] = Axes
