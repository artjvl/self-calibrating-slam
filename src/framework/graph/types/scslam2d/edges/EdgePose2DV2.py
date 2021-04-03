from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeV2 import CalibratingEdgeV2
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2


class EdgePose2DV2(CalibratingEdgeV2):
    endpoints = 1

    def __init__(
            self,
            node: NodeSE2
    ):
        super().__init__([node])

    def get_value(self) -> Supported:
        node: NodeSE2 = self.get_node(0)
        return node.get_value()
