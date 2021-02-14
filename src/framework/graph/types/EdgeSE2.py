from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.factor import *
from src.framework.graph.types import NodeSE2


class EdgeSE2(FactorEdge):

    tag = 'EDGE_SE2'
    size = 2

    # constructor
    def __init__(self, a: NodeSE2, b: NodeSE2, transformation: Optional[SE2] = None, information: Optional[Square] = None):
        if transformation is None:
            transformation = SE2.from_elements(0, 0, 0)
        super().__init__([a, b], transformation, information)

    # public methods
    def get_transformation(self) -> SE2:
        return self.get_value()

    def set_transformation(self, transformation: SE2):
        self.set_value(transformation)

    # abstract implementations
    def compute_error(self) -> Vector:
        measurement = self.get_transformation()
        a = self.get_node(0).get_value()
        b = self.get_node(1).get_value()
        distance = a.inverse() * b
        return distance.minus(measurement)

    def write(self):
        transformation = self.get_transformation()
        translation_string = self._lst_to_string(self._array_to_lst(transformation.translation()))
        rotation_string = self._lst_to_string(self._array_to_lst(transformation.rotation().vector()))
        data_string = ' '.join([translation_string, rotation_string])
        if self._is_uncertain:
            data_string += ' {}'.format(self._lst_to_string(self._symmetric_to_lst(self._information)))
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), data_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        translation = Vector(elements[:2])
        angle = elements[2]
        rotation = SO2.from_elements(angle)
        self.set_transformation(SE2(translation, rotation))
        if len(elements) != 3:
            self.set_information(self._lst_to_symmetric(elements[3:]))

    @classmethod
    def from_nodes(cls, nodes: List[NodeSE2]):
        return cls(nodes[0], nodes[1])
