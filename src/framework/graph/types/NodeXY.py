from typing import *

from src.framework.graph.factor import FactorNode
from src.framework.graph.types.Parser import Parser
from src.framework.groups import SO3, SE3
from src.framework.structures import Vector
from src.gui.viewer.Colour import Colour


class NodeXY(FactorNode[Vector]):

    tag = 'VERTEX_POINT_XY'
    is_physical = True
    has_rotation = False
    colour = Colour.GREEN

    # constructor
    def __init__(self, id: int, point: Optional[Vector] = None):
        if point is None:
            point = Vector.zeros(2)
        super().__init__(id, point)

    # getters/setters
    def get_translation(self) -> Vector:
        return self.get_value()

    def set_translation(self, point: Vector):
        self.set_value(point)

    # 3-dimensional getters
    def get_translation3(self) -> Vector:
        return self.get_translation().extend(0)

    def get_rotation3(self) -> SO3:
        pass

    def get_pose3(self) -> SE3:
        pass

    # read/write methods
    def write(self):
        translation = self.get_translation()
        string = Parser.list_to_string(Parser.array_to_list(translation))
        return ' '.join([self.tag, str(self.id()), string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        point = Vector(elements[:2])
        self.set_translation(point)
