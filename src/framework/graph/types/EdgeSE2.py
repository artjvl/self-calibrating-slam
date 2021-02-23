from typing import *

from src.framework.graph.factor import FactorEdge
from src.framework.graph.types.NodeSE2 import NodeSE2
from src.framework.graph.types.Parser import Parser
from src.framework.groups import SO2, SE2
from src.framework.structures import Vector, Square
from src.gui.viewer.Colour import Colour


class EdgeSE2(FactorEdge[SE2]):

    tag = 'EDGE_SE2'
    size = 2
    is_physical = True
    colour = Colour.CYAN

    # constructor
    def __init__(
            self,
            a: NodeSE2,
            b: NodeSE2,
            transformation: Optional[SE2] = None,
            information: Optional[Square] = None
    ):
        if transformation is None:
            transformation = SE2.from_elements(0, 0, 0)
        super().__init__([a, b], transformation, information)

    # getters/setters
    def get_transformation(self) -> SE2:
        return self.get_value()

    def set_transformation(self, transformation: SE2):
        self.set_value(transformation)

    # 3-dimensional getters
    def get_endpoints3(self) -> Tuple[Vector, Vector]:
        return self.get_node(0).get_translation3(), self.get_node(1).get_translation3()

    # error
    def compute_error_vector(self) -> Vector:
        measurement = self.get_transformation()
        a = self.get_node(0).get_value()
        b = self.get_node(1).get_value()
        distance = a.inverse() * b
        return distance.minus(measurement)

    def compute_error(self) -> float:
        return 0.

    # read/write
    def write(self):
        transformation = self.get_transformation()
        translation_string = Parser.list_to_string(Parser.array_to_list(transformation.translation()))
        rotation_string = Parser.list_to_string(Parser.array_to_list(transformation.rotation().vector()))
        data_string = ' '.join([translation_string, rotation_string])
        if self._is_uncertain:
            data_string += ' {}'.format(Parser.list_to_string(Parser.symmetric_to_list(self.get_information())))
        return ' '.join([self.tag, str(self.get_node(0).id()), str(self.get_node(1).id()), data_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        translation = Vector(elements[:2])
        angle = elements[2]
        rotation = SO2.from_elements(angle)
        self.set_transformation(SE2(translation, rotation))
        if len(elements) != 3:
            self.set_information(Parser.list_to_symmetric(elements[3:]))

    # alternative constructor
    @classmethod
    def from_nodes(cls, nodes: List[NodeSE2]):
        return cls(nodes[0], nodes[1])
