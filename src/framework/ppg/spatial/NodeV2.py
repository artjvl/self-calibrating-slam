import typing as tp

from src.framework.math.matrix.vector import Vector2
from src.framework.ppg.Graph import SpatialNode


class NodeV2(SpatialNode[Vector2]):
    _type = Vector2

    def _compute_ate2(self) -> tp.Optional[float]:
        return None
