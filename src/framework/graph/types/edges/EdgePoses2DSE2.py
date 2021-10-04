import typing as tp

from src.framework.graph.protocols.Visualisable import DrawEdge
from src.framework.graph.types.edges.CalibratingEdgeSE2 import CalibratingEdgeSE2
from src.framework.math.matrix.square import Square3
from src.framework.math.matrix.vector import Vector2
from src.gui.viewer.Rgb import RgbTuple, Rgb

if tp.TYPE_CHECKING:
    from src.framework.graph.CalibratingGraph import SubCalibratingNode
    from src.framework.graph.types.nodes.SpatialNode import NodeSE2
    from src.framework.math.lie.rotation import SO2
    from src.framework.math.lie.transformation import SE2
    from src.framework.math.matrix.vector import Vector3


class EdgePoses2DSE2(CalibratingEdgeSE2, DrawEdge):
    _num_endpoints = 2

    def __init__(
            self,
            name: tp.Optional[str] = None,
            node_a: tp.Optional['NodeSE2'] = None,
            node_b: tp.Optional['NodeSE2'] = None,
            measurement: tp.Optional['SE2'] = None,
            info_matrix: tp.Optional[Square3] = None
    ):
        nodes: tp.List['SubCalibratingNode'] = [node for node in [node_a, node_b] if node is not None]
        super().__init__(
            name=name,
            nodes=nodes,
            measurement=measurement,
            info_matrix=info_matrix
        )

    def is_complete(self) -> bool:
        return self.has_value() and len(self.get_endpoints()) == 2

    def get_delta(self) -> 'SE2':
        assert self.is_complete()
        endpoints: tp.List['NodeSE2'] = self.get_endpoints()
        a: NodeSE2 = endpoints[0]
        b: NodeSE2 = endpoints[1]
        return b.get_value() - a.get_value()

    def _compute_rpe_translation2(self) -> float:
        assert self.has_truth() and self.is_complete()
        delta: Vector2 = self.get_delta().translation() - self.get_truth().get_delta().get_translation()
        return delta[0] ** 2 + delta[1] ** 2

    def _compute_rpe_rotation2(self) -> float:
        assert self.has_truth() and self.is_complete()
        delta: 'SO2' = self.get_delta().rotation() - self.get_truth().get_delta().get_rotation()
        return delta.angle() ** 2

    # Visualisable
    def draw_nodeset(self) -> tp.Tuple['Vector3', 'Vector3']:
        vectors: tp.List['Vector3'] = [node.get_value().get_translation().to_vector3() for node in self.get_endpoints()]
        return vectors[0], vectors[1]

    @staticmethod
    def draw_rgb() -> RgbTuple:
        return Rgb.ORANGE
