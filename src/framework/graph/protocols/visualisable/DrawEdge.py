import typing as tp
from abc import abstractmethod

from src.framework.graph.protocols.Visualisable import Visualisable
from src.framework.math.matrix.vector import Vector3


class DrawEdge(Visualisable):

    @abstractmethod
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        pass
