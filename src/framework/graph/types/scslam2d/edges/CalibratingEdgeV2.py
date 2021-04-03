from abc import ABC

from src.framework.graph.FactorGraph import SubVector
from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.types.scslam2d.edges.CalibratingEdge import CalibratingEdge
from src.framework.graph.types.scslam2d.nodes.ParameterNode import SubParamNode
from src.framework.simulation.parameters.Parameter import Parameter
from src.framework.simulation.parameters.ParameterFactory import ParameterFactory
from src.framework.structures import Vector2


class CalibratingEdgeV2(CalibratingEdge, ABC):
    default_datatype = Vector2

    def get_estimate(self) -> Supported:
        value: Vector2 = self.get_value()
        estimate: Vector2 = value
        if self._paramtype is not None:
            param: SubParamNode = self.get_paramnode()
            parameter: Parameter = ParameterFactory.from_tag(param.get_interpretation())(param.get_value())
            estimate = parameter.compose_translation(value)
        return estimate

    def compute_error_vector(self) -> SubVector:
        return Vector2(self.get_estimate() - self.get_measurement())
