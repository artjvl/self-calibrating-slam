from typing import *

from src.utils import DictTree
from src.utils.DictTree import DictTreeData

ParameterType = Union[Type[str], Type[int], Type[float], Type[bool]]
Parameter = Union[str, int, float, bool]


class ParameterDictTreeData(DictTreeData):

    prefixes = {'s_': str, 'i_': int, 'f_': float, 'b_': bool}

    # constructor
    def __init__(
            self,
            key: str,
            value_string: str
    ):
        prefix: str = key[:2]
        assert prefix in self.prefixes, '{} in {}'.format(prefix, self.prefixes)

        self._name: str = key[2:]
        self._type: ParameterType = self.prefixes[prefix]
        self._value: Parameter = self._type(value_string)

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> Parameter:
        return self._value

    def set_value(self, value: Parameter):
        assert isinstance(value, self._type)
        self._value = value

    def get_type(self) -> ParameterType:
        return self._type


class ParameterDictTree(DictTree[str, ParameterDictTreeData]):

    # constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_parameter(
            self,
            key: str,
            value_string: str
    ):
        data = ParameterDictTreeData(key, value_string)
        self.add_value(data.get_name(), data)

    def get_parameters(self) -> Dict[str, Parameter]:
        parameters: Dict[str, Parameter] = {}
        for key, value in self.key_values():
            parameters[key] = value.get_value()
        return parameters

    def set_parameter(
            self,
            name: str,
            value: Parameter
    ):
        data: ParameterDictTreeData = self[name].get_value()
        data.set_value(value)
