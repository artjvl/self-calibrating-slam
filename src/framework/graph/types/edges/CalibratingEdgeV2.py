from abc import ABC

from src.framework.graph.CalibratingGraph import CalibratingEdge
from src.framework.graph.types.ParameterComposer import ParameterComposer
from src.framework.math.matrix.vector import Vector2


class CalibratingEdgeV2(CalibratingEdge[Vector2], ABC):

    _type = Vector2

    def get_estimate(self) -> Vector2:
        estimate: Vector2 = self.get_value()
        for parameter in self.get_parameters():
            estimate = ParameterComposer.translate_with_parameter(parameter, estimate, inverse=True)
        return estimate

    def compute_error_vector(self) -> Vector2:
        return Vector2(self.get_estimate().array() - self.get_measurement().array())
