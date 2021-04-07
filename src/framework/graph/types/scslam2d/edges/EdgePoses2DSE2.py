import typing as tp

from src.framework.graph.protocols.Visualisable import Visualisable
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.scslam2d.nodes.typological.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3


class EdgePoses2DSE2(CalibratingEdgeSE2, Visualisable):
    _num_endpoints = 2

    def __init__(
            self,
            *nodes: NodeSE2
    ):
        if nodes:
            assert isinstance(nodes[0], NodeSE2)
            assert isinstance(nodes[1], NodeSE2)
        super().__init__(*nodes)

    def get_value(self) -> SE2:
        a: NodeSE2
        b: NodeSE2
        a, b = tuple(self.get_endpoints())
        return a.get_value() - b.get_value()

    def draw_endpoints(self) -> tp.Optional[tp.List[Vector3]]:
        return [node.get_value().translation().to_v3() for node in self.get_endpoints()]
