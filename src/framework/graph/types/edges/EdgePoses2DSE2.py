import typing as tp

from src.framework.graph.protocols.visualisable.DrawEdge import DrawEdge
from src.framework.graph.types.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.math.lie.rotation import SO2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb


class EdgePoses2DSE2(CalibratingEdgeSE2, DrawEdge):
    _num_topological = 2

    def __init__(
            self,
            value: tp.Optional[SE2] = None,
            info_matrix: tp.Optional[Square3] = None,
            node_a: tp.Optional[NodeSE2] = None,
            node_b: tp.Optional[NodeSE2] = None
    ):
        nodes = list(filter(lambda n: n is not None, [node_a, node_b]))
        super().__init__(value, info_matrix, *nodes)

    def get_value(self) -> SE2:
        a: NodeSE2
        b: NodeSE2
        a, b = tuple(self.get_endpoints())
        return b.get_value() - a.get_value()

    def compute_rpe_translation2(self) -> float:
        assert self.has_true()
        delta: Vector2 = self.get_value().translation() - self.get_true().get_value().translation()
        return delta[0]**2 + delta[1]**2

    def compute_rpe_rotation(self) -> float:
        assert self.has_true()
        delta: SO2 = self.get_value().rotation() - self.get_true().get_value().rotation()
        return delta.angle()

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        def get_node(node) -> Vector3: return node.get_value().translation().to_vector3()
        a, b = tuple(self.get_endpoints())
        return get_node(a), get_node(b)

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.ORANGE