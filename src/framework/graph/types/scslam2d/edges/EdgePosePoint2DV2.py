from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.scslam2d.nodes import NodeV2
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2
from src.framework.structures import Vector2


class EdgePosePoint2DV2(CalibratingEdgeSE2):
    endpoints = 2

    def __init__(
            self,
            a: NodeSE2,
            b: NodeV2
    ):
        super().__init__([a, b])

    def get_value(self) -> Supported:
        a: NodeSE2 = self.get_node(0)
        b: NodeV2 = self.get_node(1)
        return Vector2(b.get_value() - a.get_value().translation())
