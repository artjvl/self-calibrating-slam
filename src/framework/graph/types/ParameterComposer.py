import enum
import typing as tp

import numpy as np
from src.framework.math.lie.transformation import SE2
from src.framework.math.matrix.vector import Vector2
from src.framework.math.matrix.vector import Vector3
from utils.TwoWayDict import TwoWayDict

if tp.TYPE_CHECKING:
    from src.framework.graph.types.nodes.ParameterNode import SubParameterNode


class ParameterType(enum.Enum):
    BIAS = 'bias'
    OFFSET = 'offset'
    SCALE = 'scale'


class ParameterDict(object):
    _parameters: TwoWayDict = TwoWayDict()
    for interpretation in ParameterType:
        _parameters[interpretation] = interpretation.value

    @classmethod
    def from_string(cls, interpretation: str) -> ParameterType:
        assert interpretation in cls._parameters
        return cls._parameters[interpretation]

    @classmethod
    def from_interpretation(cls, interpretation: ParameterType) -> str:
        assert interpretation in cls._parameters
        return cls._parameters[interpretation]


class ParameterComposer(object):

    @staticmethod
    def transform_bias(
            transformation: SE2,
            parameter: Vector3,
            inverse: bool = False
    ) -> SE2:
        if inverse:
            parameter = - parameter
        return transformation * SE2.from_translation_angle_vector(parameter)

    @staticmethod
    def transform_offset(
            transformation: SE2,
            parameter: Vector3,
            inverse: bool = False
    ) -> SE2:
        if inverse:
            parameter = - parameter
        offset: SE2 = SE2.from_translation_angle_vector(parameter)
        return offset * transformation * offset.inverse()

    @staticmethod
    def transform_scale(
            transformation: SE2,
            parameter: Vector3,
            inverse: bool = False
    ) -> SE2:
        if inverse:
            parameter = - parameter
        return SE2.from_translation_angle_vector(
            Vector3(np.multiply(parameter.array(), transformation.translation_angle_vector().array()))
        )

    @classmethod
    def transform(
            cls,
            interpretation: ParameterType,
            transformation: SE2,
            parameter: Vector3,
            inverse: bool = False
    ) -> SE2:
        if interpretation == ParameterType.BIAS:
            return cls.transform_bias(transformation, parameter, inverse)
        elif interpretation == ParameterType.OFFSET:
            return cls.transform_offset(transformation, parameter, inverse)
        elif interpretation == ParameterType.SCALE:
            return cls.transform_scale(transformation, parameter, inverse)
        return transformation

    @classmethod
    def translate(
            cls,
            interpretation: ParameterType,
            translation: Vector2,
            parameter: Vector3,
            inverse: bool = False
    ) -> Vector2:
        pose: SE2 = SE2.from_translation_angle(translation, 0.)
        transformed: SE2 = cls.transform(interpretation, pose, parameter, inverse)
        return transformed.translation()

    @classmethod
    def transform_with_parameter(
            cls,
            parameter: 'SubParameterNode',
            transformation: SE2,
            inverse: bool = False
    ) -> SE2:
        return cls.transform(parameter.get_interpretation(), transformation, parameter.to_vector3(), inverse)

    @classmethod
    def translate_with_parameter(
            cls,
            parameter: 'SubParameterNode',
            translation: Vector2,
            inverse: bool = False
    ) -> Vector2:
        return cls.translate(parameter.get_interpretation(), translation, parameter.to_vector3(), inverse)
