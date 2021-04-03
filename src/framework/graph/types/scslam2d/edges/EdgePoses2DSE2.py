from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.scslam2d.nodes.NodeSE2 import NodeSE2


class EdgePoses2DSE2(CalibratingEdgeSE2):
    endpoints = 2

    def __init__(
            self,
            a: NodeSE2,
            b: NodeSE2
    ):
        super().__init__([a, b])

    def get_value(self) -> Supported:
        a: NodeSE2 = self.get_node(0)
        b: NodeSE2 = self.get_node(1)
        return a.get_value().inverse() * b.get_value()
