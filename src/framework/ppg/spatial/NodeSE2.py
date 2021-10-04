import typing as tp

from src.framework.math.lie.transformation import SE2
from src.framework.ppg.Graph import SpatialNode

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector2


class NodeSE2(SpatialNode[SE2]):
    _type = SE2

    def _compute_ate2(self) -> tp.Optional[float]:
        assert self.has_truth()
        delta: 'Vector2' = self.get_truth().get_value().get_translation() - self.get_value().get_translation()
        return delta[0] ** 2 + delta[1] ** 2
