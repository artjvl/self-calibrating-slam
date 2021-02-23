from typing import *

from src.framework.graph.factor import FactorNode
from src.framework.graph.types.Parser import Parser
from src.framework.groups import SO2, SE2, SO3, SE3
from src.framework.structures import Vector


class NodeSE2(FactorNode[SE2]):

    tag = 'VERTEX_SE2'
    is_physical = True
    has_rotation = True

    # constructor
    def __init__(self, id: int, pose: Optional[SE2] = None):
        if pose is None:
            pose = SE2.from_elements(0, 0, 0)
        super().__init__(id, pose)

    # getters/setters
    def get_pose(self) -> SE2:
        return self.get_value()

    def set_pose(self, pose: SE2):
        self.set_value(pose)

    # abstract implementations
    def get_translation(self) -> Vector:
        return self.get_pose().translation()

    # 3-dimensional getters
    def get_translation3(self) -> Vector:
        return self.get_translation().extend(0)

    def get_rotation3(self) -> SO3:
        return self.get_pose().rotation().to_so3()

    def get_pose3(self) -> SE3:
        return self.get_pose().to_se3()

    # read/write methods
    def write(self):
        pose = self.get_pose()
        translation_string = Parser.list_to_string(Parser.array_to_list(pose.translation()))
        rotation_string = Parser.list_to_string(Parser.array_to_list(pose.rotation().vector()))
        return ' '.join([self.tag, str(self.id()), translation_string, rotation_string])

    def read(self, words: List[str]):
        elements = [float(word) for word in words]
        translation = Vector(elements[:2])
        angle = elements[2]
        rotation = SO2.from_elements(angle)
        self.set_pose(SE2(translation, rotation))
