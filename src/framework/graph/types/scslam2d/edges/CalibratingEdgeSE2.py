from abc import ABC

from src.framework.graph.types.scslam2d.edges.CalibratingEdge import CalibratingEdge
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3


class CalibratingEdgeSE2(CalibratingEdge[SE2], ABC):

    _type = SE2

    def get_estimate(self) -> SE2:
        estimate: SE2 = self.get_value()
        for parameter in self.get_parameters():
            estimate = parameter.compose_transformation(estimate, inverse=True)
        return estimate

    def compute_error_vector(self) -> Vector3:
        return self.get_estimate().minus(self.get_measurement())
