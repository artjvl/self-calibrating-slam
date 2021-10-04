import enum

from src.utils.TwoWayDict import TwoWayDict


class ParameterSpecification(enum.Enum):
    BIAS = 'bias'
    OFFSET = 'offset'
    SCALE = 'scale'


class ParameterDict(object):
    _parameters: TwoWayDict = TwoWayDict()
    for specification in ParameterSpecification:
        _parameters[specification] = specification.value

    @classmethod
    def from_string(cls, string: str) -> ParameterSpecification:
        assert string in cls._parameters
        return cls._parameters[string]

    @classmethod
    def from_specification(cls, specification: ParameterSpecification) -> str:
        assert specification in cls._parameters
        return cls._parameters[specification]
