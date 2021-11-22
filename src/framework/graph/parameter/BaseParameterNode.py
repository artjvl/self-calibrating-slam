import typing as tp

import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector3
from src.framework.graph.Graph import ParameterNode
from src.framework.graph.parameter.ParameterSpecification import ParameterSpecification

if tp.TYPE_CHECKING:
    from src.framework.graph.data.DataFactory import Quantity


def compose_bias(
        transformation: SE2,
        parameter: SE2,
        is_inverse: bool
) -> SE2:
    if is_inverse:
        parameter = parameter.inverse()
    composed: SE2 = transformation * parameter
    return composed


def compose_offset(
        transformation: SE2,
        parameter: SE2,
        is_inverse: bool
) -> SE2:
    if is_inverse:
        parameter = parameter.inverse()
    composed: SE2 = parameter * transformation * parameter.inverse()
    return composed


def compose_scale(
        transformation: SE2,
        parameter: Vector3,
        is_inverse: bool
) -> SE2:
    if is_inverse:
        parameter = Vector3(np.reciprocal(parameter.array()))
    composed: SE2 = SE2.from_translation_angle_vector(
        Vector3(np.multiply(parameter.array(), transformation.translation_angle_vector().array()))
    )
    return composed


T = tp.TypeVar('T')


class BaseParameterNode(tp.Generic[T], ParameterNode[T]):

    def __init__(
            self,
            name: tp.Optional[str],
            value: tp.Optional['Quantity'],
            specification: ParameterSpecification,
            id_: int = 0,
            timestep: int = 0,
            index: int = 0
    ):
        assert specification in [
            ParameterSpecification.BIAS,
            ParameterSpecification.OFFSET,
            ParameterSpecification.SCALE
        ]
        super().__init__(
            name, value, specification,
            id_=id_, timestep=timestep, index=index)

    def compose_transformation(
            self,
            transformation: SE2,
            is_inverse: bool = False
    ) -> SE2:
        if self.get_specification() == ParameterSpecification.BIAS:
            return self._compose_as_bias(transformation, is_inverse)
        if self.get_specification() == ParameterSpecification.OFFSET:
            return self._compose_as_offset(transformation, is_inverse)
        if self.get_specification() == ParameterSpecification.SCALE:
            return self._compose_as_scale(transformation, is_inverse)

    def _compose_as_bias(
            self,
            transformation: SE2,
            is_inverse: bool = False
    ) -> SE2:
        bias = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_bias(transformation, bias, is_inverse)

    def _compose_as_offset(
            self,
            transformation: SE2,
            is_inverse: bool = False
    ) -> SE2:
        offset = SE2.from_translation_angle_vector(self.to_vector3())
        return compose_offset(transformation, offset, is_inverse)

    def _compose_as_scale(
            self,
            transformation: SE2,
            is_inverse: bool = False
    ) -> SE2:
        scale = self.to_vector3()
        return compose_scale(transformation, scale, is_inverse)
