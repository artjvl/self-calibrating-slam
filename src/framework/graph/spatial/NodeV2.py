import typing as tp

from src.framework.graph.Graph import SpatialNode
from src.framework.graph.Visualisable import DrawPoint
from src.framework.math.matrix.vector import Vector2

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector3


class NodeV2(SpatialNode[Vector2], DrawPoint):
    _type = Vector2

    def _compute_ate2(self) -> tp.Optional[float]:
        return None

    def draw_point(self) -> 'Vector3':
        return self.get_value().to_vector3()
