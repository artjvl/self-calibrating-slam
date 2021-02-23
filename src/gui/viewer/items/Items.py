from enum import Enum
from typing import Type

from src.gui.viewer.items import Points, Edges, Axes
from src.gui.viewer.items.GraphicsItem import GraphicsItem


class Items(Enum):
    POINTS: Type[GraphicsItem] = Points
    EDGES: Type[GraphicsItem] = Edges
    AXES: Type[GraphicsItem] = Axes
