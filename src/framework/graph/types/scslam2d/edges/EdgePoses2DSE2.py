import typing as tp

from src.framework.graph.protocols.visualisable.DrawEdge import DrawEdge
from src.framework.graph.types.scslam2d.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.scslam2d.nodes.topological.NodeSE2 import NodeSE2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb


class EdgePoses2DSE2(CalibratingEdgeSE2, DrawEdge):
    _num_endpoints = 2

    def __init__(
            self,
            *nodes: NodeSE2
    ):
        if nodes:
            assert len(nodes) == 2
            assert isinstance(nodes[0], NodeSE2)
            assert isinstance(nodes[1], NodeSE2)
        super().__init__(*nodes)

    def get_value(self) -> SE2:
        a: NodeSE2
        b: NodeSE2
        a, b = tuple(self.get_endpoints())
        return b.get_value() - a.get_value()

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        def get_node(node) -> Vector3: return node.get_value().translation().to_vector3()
        a, b = tuple(self.get_endpoints())
        return get_node(a), get_node(b)

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.ORANGE
