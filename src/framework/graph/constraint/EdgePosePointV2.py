import typing as tp

from src.framework.math.matrix.vector import Vector2
from src.framework.graph.constraint.EdgeV2 import EdgeV2
from src.framework.graph.spatial.NodeV2 import NodeV2

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.square import SubSquare
    from src.framework.graph.Graph import SubSpatialNode
    from src.framework.graph.spatial.NodeSE2 import NodeSE2


class EdgePosePointV2(EdgeV2):
    _type = Vector2
    _cardinality = 2

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[Vector2] = None,
            info_matrix: tp.Optional['SubSquare'] = None,
            node_a: tp.Optional['NodeSE2'] = None,
            node_b: tp.Optional['NodeV2'] = None
    ):
        nodes: tp.List['SubSpatialNode'] = []
        if node_a is not None:
            nodes.append(node_a)
        if node_b is not None:
            nodes.append(node_b)
        super().__init__(
            name,
            value=value, info_matrix=info_matrix, nodes=nodes
        )

    # measurement model
    def delta(self) -> Vector2:
        assert self._is_complete()
        spatial_nodes: tp.List['NodeSE2'] = self.get_spatial_nodes()
        a: 'NodeSE2' = spatial_nodes[0]
        b: 'NodeV2' = spatial_nodes[1]
        return Vector2(b.get_value() - a.get_value().translation())

    # metrics
    def _compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def _compute_rpe_rotation2(self) -> tp.Optional[float]:
        return None