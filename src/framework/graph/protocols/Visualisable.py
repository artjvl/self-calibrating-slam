import typing as tp

from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector3


class Visualisable(object):

    def draw_pose(self) -> tp.Optional[SE3]:
        return None

    def draw_position(self) -> tp.Optional[Vector3]:
        return None

    def draw_endpoints(self) -> tp.Optional[tp.List[Vector3]]:
        return None
