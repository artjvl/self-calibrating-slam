from typing import *

from src.framework.groups import SO3
from src.framework.structures import *
from src.framework.graph.factor import *


class NodeXY(FactorNode[Vector]):

    tag = 'VERTEX_POINT_XY'
    has_rotation = False

    # constructor
    def __init__(self, id: int, point: Optional[Vector] = None):
        if point is None:
            point = Vector.zeros(2)
        super().__init__(id, point)

    # public methods
    def get_point(self) -> Vector:
        return self.get_value()

    def set_point(self, point: Vector):
        self.set_value(point)

    # abstract implementations
    def write(self):
        point = self.get_point()
        string = self._lst_to_string(self._array_to_lst(point))
        return ' '.join([self.tag, str(self.id()), string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        point = Vector(elements[:2])
        self.set_point(point)

    def get_point3(self) -> Vector:
        return self.get_point().extend(0)

    def get_rotation3(self) -> SO3:
        pass
