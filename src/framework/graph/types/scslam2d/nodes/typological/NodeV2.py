import typing as tp

from src.framework.graph.types.scslam2d.nodes.CalibratingNode import CalibratingNode
from src.framework.math.matrix.vector import Vector2, Vector3


class NodeV2(CalibratingNode[Vector2]):

    _type = Vector2

    def draw_position(self) -> tp.Optional[Vector3]:
        return self.get_value().to_vector3()