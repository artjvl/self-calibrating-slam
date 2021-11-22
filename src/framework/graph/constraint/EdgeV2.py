from abc import ABC

from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.graph.Graph import Edge


class EdgeV2(Edge[Vector2], ABC):
    _type = Vector2

    def set_from_transformation(
            self,
            transformation: SE2
    ) -> None:
        self.set_value(transformation.translation())

    def to_transformation(self) -> SE2:
        return SE2.from_translation_angle(self.get_value(), 0.)

    def estimate(self) -> Vector2:
        delta: Vector2 = self.delta()
        transformation: SE2 = SE2.from_translation_angle(delta, 0.)
        for parameter in self.get_parameter_nodes():
            transformation = parameter.compose_transformation(transformation, is_inverse=True)
        return transformation.translation()

    def _compute_error_vector(self) -> Vector2:
        return self.estimate() - self.get_value()
