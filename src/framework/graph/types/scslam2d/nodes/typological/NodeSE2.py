from src.framework.graph.protocols.visualisable.DrawAxis import DrawAxis
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.lie.transformation import SE2, SE3


class NodeSE2(CalibratingNode[SE2], DrawAxis):
    _type = SE2

    def draw_pose(self) -> SE3:
        return self.get_value().to_se3()
