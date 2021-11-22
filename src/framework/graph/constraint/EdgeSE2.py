import typing as tp
from abc import ABC

from src.framework.math.lie.transformation import SE2
from src.framework.graph.Graph import Edge

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector3


class EdgeSE2(Edge[SE2], ABC):
    _type = SE2

    def set_from_transformation(
            self,
            transformation: SE2
    ) -> None:
        self.set_value(transformation)

    def to_transformation(self) -> SE2:
        return self.get_value()

    def estimate(self) -> SE2:
        transformation: SE2 = self.delta()
        for parameter in self.get_parameter_nodes():
            transformation = parameter.compose_transformation(transformation, is_inverse=True)
        return transformation

    def _compute_error_vector(self) -> 'Vector3':
        error: SE2 = self.estimate() - self.get_value()
        error_vector: 'Vector3' = error.translation_angle_vector()
        return error_vector
