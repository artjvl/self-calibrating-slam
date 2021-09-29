import typing as tp

from src.framework.graph.CalibratingGraph import SubCalibratingNode
from src.framework.graph.protocols.Visualisable import DrawEdge
from src.framework.graph.types.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.graph.types.nodes.SpatialNode import NodeSE2
from src.framework.math.lie.rotation import SO2
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import RgbTuple, Rgb


class EdgePoses2DSE2(CalibratingEdgeSE2, DrawEdge):
    _num_endpoints = 2

    def __init__(
            self,
            name: tp.Optional[str] = None,
            node_a: tp.Optional[NodeSE2] = None,
            node_b: tp.Optional[NodeSE2] = None,
            measurement: tp.Optional[SE2] = None,
            info_matrix: tp.Optional[Square3] = None
    ):
        nodes: tp.List[SubCalibratingNode] = [node for node in [node_a, node_b] if node is not None]
        super().__init__(
            name=name,
            nodes=nodes,
            measurement=measurement,
            info_matrix=info_matrix,
        )

    def get_delta(self) -> SE2:
        a: NodeSE2
        b: NodeSE2
        a, b = tuple(self.get_endpoints())
        return b.get_value() - a.get_value()

    def _compute_rpe_translation2(self) -> float:
        assert self.has_truth()
        delta: Vector2 = self.get_delta().translation() - self.get_truth().get_delta().translation()
        return delta[0]**2 + delta[1]**2

    def _compute_rpe_rotation2(self) -> float:
        assert self.has_truth()
        delta: SO2 = self.get_delta().rotation() - self.get_truth().get_delta().rotation()
        return delta.angle() ** 2

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple[Vector3, Vector3]:
        def get_node(node) -> Vector3: return node.get_value().translation().to_vector3()
        a, b = tuple(self.get_endpoints())
        return get_node(a), get_node(b)

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.ORANGE
