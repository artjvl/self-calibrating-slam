import typing as tp

from src.framework.graph.protocols.Visualisable import Visualisable
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.lie.transformation import SE2, SE3
from src.framework.math.matrix.vector import Vector3


class NodeSE2(CalibratingNode[SE2], Visualisable):

    _type = SE2

    def draw_pose(self) -> tp.Optional[SE3]:
        return self.get_value().to_se3()

    def draw_position(self) -> tp.Optional[Vector3]:
        return self.get_value().translation().to_vector3()
