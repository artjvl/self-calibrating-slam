from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.factor import *
from src.framework.graph.types import NodeSE2, NodeXY


class EdgeSE2XY(FactorEdge[Vector]):

    tag = 'EDGE_SE2_POINT_XY'
    size = 2

    # constructor
    def __init__(self, a: NodeSE2, b: NodeXY, distance: Optional[Vector] = None, information: Optional[Square] = None):
        if distance is None:
            distance = Vector.zeros(2)
        super().__init__([a, b], distance, information)

    # public methods
    def get_distance(self) -> Vector:
        return self.get_value()

    def set_distance(self, distance: Vector):
        self.set_value(distance)

    # abstract implementations
    def compute_error(self) -> Vector:
        measurement = self.get_distance()
        a = self.get_node(0).get_value()
        xy = self.get_node(1).get_value()
        b = SE2.from_vectors(xy, Vector(0))
        distance = (a.inverse() * b).translation()
        return distance - measurement

    def write(self):
        distance = self.get_distance()
        data_string = self._lst_to_string(self._array_to_lst(distance))
        if self._is_uncertain:
            data_string += ' {}'.format(self._lst_to_string(self._symmetric_to_lst(self._information)))
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), data_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        distance = Vector(elements[:2])
        self.set_distance(distance)
        if len(elements) != 2:
            self.set_information(self._lst_to_symmetric(elements[2:]))

    @classmethod
    def from_nodes(cls, nodes: list):
        return cls(nodes[0], nodes[1])
