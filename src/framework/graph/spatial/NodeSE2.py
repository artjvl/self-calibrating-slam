import typing as tp

from src.framework.graph.Graph import SpatialNode
from src.framework.graph.Visualisable import DrawAxis
from src.framework.math.lie.transformation import SE2

if tp.TYPE_CHECKING:
    from src.framework.math.lie.transformation import SE3
    from src.framework.math.matrix.vector import Vector2


class NodeSE2(SpatialNode[SE2], DrawAxis):
    _type = SE2

    def _compute_ate2(self) -> tp.Optional[float]:
        assert self.has_truth()
        delta: 'Vector2' = self.get_truth().get_value().translation() - self.get_value().translation()
        return delta[0] ** 2 + delta[1] ** 2

    def draw_pose(self) -> 'SE3':
        return self.get_value().to_se3()