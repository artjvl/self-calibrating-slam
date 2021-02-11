from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.framework.graph.factor import *


class NodeSE2(FactorNode):

    tag = 'VERTEX_SE2'

    # constructor
    def __init__(self, id: int, pose: Optional[SE2] = None):
        if pose is None:
            pose = SE2.from_elements(0, 0, 0)
        super().__init__(id, pose)

    # public methods
    def get_pose(self) -> SE2:
        return self.get_value()

    def set_pose(self, pose: SE2):
        self.set_value(pose)

    # abstract implementations
    def write(self):
        pose = self.get_pose()
        translation_string = self._lst_to_string(self._array_to_lst(pose.translation()))
        rotation_string = self._lst_to_string(self._array_to_lst(pose.rotation().vector()))
        return ' '.join([self.tag, str(self.id()), translation_string, rotation_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        translation = Vector(elements[:2])
        angle = elements[2]
        rotation = SO2.from_elements(angle)
        self.set_pose(SE2(translation, rotation))
