from abc import abstractmethod

from src.framework.graph.protocols.Visualisable import Visualisable
from src.framework.math.matrix.vector import Vector3


class DrawPoint(Visualisable):

    @abstractmethod
    def draw_point(self) -> Vector3:
        pass
