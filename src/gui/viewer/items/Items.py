from enum import Enum
from typing import Type

from src.gui.viewer.items.Axes import Axes
from src.gui.viewer.items.Edges import Edges
from src.gui.viewer.items.GraphicsItem import SubGraphicsItem
from src.gui.viewer.items.Points import Points


class Items(Enum):
    POINTS: Type[SubGraphicsItem] = Points
    EDGES: Type[SubGraphicsItem] = Edges
    AXES: Type[SubGraphicsItem] = Axes
