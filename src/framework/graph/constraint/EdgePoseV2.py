import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.graph.constraint.EdgeV2 import EdgeV2

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.square import SubSquare
    from src.framework.graph.Graph import SubSpatialNode
    from src.framework.graph.spatial.NodeSE2 import NodeSE2


class EdgePoseV2(EdgeV2):
    _type = Vector2
    _cardinality = 1

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[Vector2] = None,
            info_matrix: tp.Optional['SubSquare'] = None,
            node: tp.Optional['NodeSE2'] = None
    ):
        nodes: tp.List['SubSpatialNode'] = []
        if node is not None:
            nodes.append(node)
        super().__init__(
            name,
            value=value, info_matrix=info_matrix, nodes=nodes
        )

    # measurement model
    def delta(self) -> SE2:
        assert self._is_complete()
        node: 'NodeSE2' = self.get_spatial_nodes()[0]
        return node.get_value().translation()

    # metrics
    def _compute_rpe_translation2(self) -> tp.Optional[float]:
        return None

    def _compute_rpe_rotation2(self) -> tp.Optional[float]:
        return None
