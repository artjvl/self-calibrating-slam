from abc import ABC

from src.framework.graph.CalibratingGraph import CalibratingEdge
from src.framework.graph.protocols.Measurement import Measurement2D
from src.framework.math.matrix.vector import Vector2


class CalibratingEdgeV2(CalibratingEdge[Vector2], ABC):

    _type = Vector2

    def get_estimate(self) -> Vector2:
        estimate: Measurement2D = Measurement2D.from_translation(self.get_delta())
        for parameter in self.get_parameters():
            estimate = parameter.compose(estimate, is_inverse=True)
        return estimate.translation()

    def _compute_error_vector(self) -> Vector2:
        return Vector2(self.get_estimate().array() - self.get_value().array())

    def set_measurement(self, measurement: Measurement2D) -> None:
        self.set_value(measurement.translation())

    def get_measurement(self) -> Measurement2D:
        return Measurement2D.from_translation(self.get_value())
