from abc import ABC

from src.framework.graph.types.ParameterComposer import ParameterComposer, ParameterType
from src.framework.graph.CalibratingGraph import CalibratingEdge
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3


class CalibratingEdgeSE2(CalibratingEdge[SE2], ABC):

    _type = SE2

    def get_estimate(self) -> SE2:
        estimate: SE2 = self.get_value()
        for parameter in self.get_parameters():
            estimate = ParameterComposer.transform_with_parameter(parameter, estimate, inverse=True)
        return estimate

    def compute_error_vector(self) -> Vector3:
        delta: SE2 = self.get_estimate() - self.get_measurement()
        return delta.translation_angle_vector()
        # return self.get_estimate().minus(self.get_measurement())
