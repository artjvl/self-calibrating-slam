from abc import abstractmethod

from src.framework.graph.protocols.visualisable.DrawPoint import DrawPoint
from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector3


class DrawAxis(DrawPoint):

    @abstractmethod
    def draw_pose(self) -> SE3:
        pass

    def draw_point(self) -> Vector3:
        pose = self.draw_pose()
        return pose.translation()
