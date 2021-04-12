from src.framework.graph.types.scslam2d.edges.CalibratingEdgeV2 import CalibratingEdgeV2
from src.framework.graph.types.scslam2d.nodes.typological.NodeSE2 import NodeSE2
from src.framework.math.matrix.vector import Vector2


class EdgePose2DV2(CalibratingEdgeV2):
    _num_endpoints = 1

    def __init__(
            self,
            *nodes: NodeSE2
    ):
        if nodes:
            assert isinstance(nodes[0], NodeSE2)
        super().__init__(*nodes)

    def get_value(self) -> Vector2:
        node: NodeSE2
        node, = tuple(self.get_endpoints())
        return node.get_value()
