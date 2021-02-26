from typing import *

from src.framework.graph.factor.FactorEdge import FactorEdge
from src.framework.graph.types.NodeSE2 import NodeSE2
from src.framework.graph.types.NodeXY import NodeXY
from src.framework.graph.types.Parser import Parser
from src.framework.groups import SE2
from src.framework.structures import Vector, Square
from src.gui.viewer.Colour import Colour


class EdgeSE2XY(FactorEdge[Vector]):

    tag = 'EDGE_SE2_XY'
    size = 2
    is_physical = True
    colour = Colour.ORANGE

    # constructor
    def __init__(
            self,
            a: NodeSE2,
            b: NodeXY,
            distance: Optional[Vector] = None,
            information: Optional[Square] = None
    ):
        if distance is None:
            distance = Vector.zeros(2)
        super().__init__([a, b], distance, information)

    # getters/setters
    def get_distance(self) -> Vector:
        return self.get_value()

    def set_distance(self, distance: Vector):
        self.set_value(distance)

    # 3-dimensional getter
    def get_endpoints3(self):
        return self.get_node(0).get_translation3(), self.get_node(1).get_translation3()

    # error
    def compute_error_vector(self) -> Vector:
        measurement = self.get_distance()
        a = self.get_node(0).get_value()
        xy = self.get_node(1).get_value()
        b = SE2.from_vectors(xy, Vector(0.))
        distance = (a.inverse() * b).translation()
        return distance - measurement

    def compute_error(self) -> float:
        return 0.

    # read/write methods
    def write(self):
        distance = self.get_distance()
        data_string = Parser.list_to_string(Parser.array_to_list(distance))
        if self._is_uncertain:
            data_string += ' {}'.format(Parser.list_to_string(Parser.symmetric_to_list(self._information)))
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), data_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        distance = Vector(elements[:2])
        self.set_distance(distance)
        if len(elements) != 2:
            self.set_information(Parser.list_to_symmetric(elements[2:]))

    # alternative constructor
    @classmethod
    def from_nodes(cls, nodes: list):
        return cls(nodes[0], nodes[1])
