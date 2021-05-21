from src.framework.graph.protocols.visualisable.DrawAxis import DrawAxis
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.lie.transformation import SE2, SE3
from src.framework.math.matrix.vector import Vector2


class NodeSE2(CalibratingNode[SE2], DrawAxis):
    _type = SE2

    def draw_pose(self) -> SE3:
        return self.get_value().to_se3()

    def compute_ate2(self) -> float:
        assert self.has_true()
        delta: Vector2 = self.get_true().get_value().translation() - self.get_value().translation()
        return delta[0]**2 + delta[1]**2
