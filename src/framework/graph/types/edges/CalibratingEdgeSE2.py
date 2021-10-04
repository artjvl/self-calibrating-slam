import typing as tp
from abc import ABC

from src.framework.graph.CalibratingGraph import CalibratingEdge
from src.framework.graph.protocols.Measurement import Measurement2D
from src.framework.math.lie.transformation import SE2

if tp.TYPE_CHECKING:
    from src.framework.math.matrix.vector import Vector3
    from src.framework.graph.protocols.Measurement import SubMeasurement2D


class CalibratingEdgeSE2(CalibratingEdge[SE2], ABC):

    _type = SE2

    def get_estimate(self) -> SE2:
        estimate: 'SubMeasurement2D' = Measurement2D.from_transformation(self.get_delta())
        for parameter in self.get_parameters():
            estimate = parameter.compose(estimate, is_inverse=True)
        return estimate.get_transformation()

    def _compute_error_vector(self) -> 'Vector3':
        delta: SE2 = self.get_estimate() - self.get_value()
        translation_angle_vector: 'Vector3' = delta.translation_angle_vector()
        return translation_angle_vector
        # return self.get_estimate().minus(self.get_measurement())

    def set_measurement(self, measurement: 'SubMeasurement2D') -> None:
        self.set_value(measurement.get_transformation())

    def get_measurement(self) -> 'SubMeasurement2D':
        return Measurement2D.from_transformation(self.get_value())
