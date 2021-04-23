from src.framework.graph.types.scslam2d.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.scslam2d.nodes.CalibratingNode import SubCalibratingNode
from src.framework.graph.types.scslam2d.nodes.topological import NodeV2
from src.framework.graph.types.scslam2d.nodes.topological.NodeSE2 import NodeSE2
from src.framework.math.matrix.vector import Vector2


class EdgePosePoint2DV2(CalibratingEdgeSE2):
    _num_endpoints = 2

    def __init__(
            self,
            *nodes: SubCalibratingNode
    ):
        if nodes:
            assert isinstance(nodes[0], NodeSE2)
            assert isinstance(nodes[1], NodeV2)
        super().__init__(*nodes)

    def get_value(self) -> Vector2:
        a: NodeSE2
        b: NodeV2
        a, b = tuple(self.get_endpoints())
        return Vector2(b.get_value() - a.get_value().translation())
