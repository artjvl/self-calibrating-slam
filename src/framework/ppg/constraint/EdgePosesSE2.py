import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.ppg.constraint.EdgeSE2 import EdgeSE2

if tp.TYPE_CHECKING:
    from src.framework.math.lie.rotation import SO2
    from src.framework.math.matrix.square import SubSquare
    from src.framework.math.matrix.vector import Vector2
    from src.framework.ppg.Graph import SubSpatialNode
    from src.framework.ppg.spatial.NodeSE2 import NodeSE2


class EdgePosesSE2(EdgeSE2):
    _type = SE2
    _cardinality = 2

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional[SE2] = None,
            info_matrix: tp.Optional['SubSquare'] = None,
            node_a: tp.Optional['NodeSE2'] = None,
            node_b: tp.Optional['NodeSE2'] = None
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
    def delta(self) -> SE2:
        assert self._is_complete()
        spatial_nodes: tp.List['NodeSE2'] = self.get_spatial_nodes()
        a: 'NodeSE2' = spatial_nodes[0]
        b: 'NodeSE2' = spatial_nodes[1]
        return b.get_value() - a.get_value()

    # metrics
    def _is_complete(self) -> bool:
        return len(self.get_spatial_nodes()) == 2

    def _compute_rpe_translation2(self) -> tp.Optional[float]:
        assert self.has_truth() and self._is_complete()
        delta: 'Vector2' = self.delta().translation() - self.get_truth().delta().translation()
        return delta[0] ** 2 + delta[1] ** 2

    def _compute_rpe_rotation2(self) -> tp.Optional[float]:
        assert self.has_truth() and self.is_complete()
        delta: 'SO2' = self.delta().rotation() - self.get_truth().delta().rotation()
        return delta.angle() ** 2
