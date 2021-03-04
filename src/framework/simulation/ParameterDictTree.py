from typing import *

from src.utils import DictTree
from src.utils.DictTree import DictTreeData


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
        self._type: Union[Type[str], Type[int], Type[float], Type[bool]] = self.prefixes[prefix]
        self._value: Union[str, int, float, bool] = self._type(value_string)

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> Union[str, int, float, bool]:
        return self._value

    def get_type(self) -> Union[Type[str], Type[int], Type[float], Type[bool]]:
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

    def get_parameters(self) -> Dict[str, Union[str, int, float, bool]]:
        parameters: Dict[str, Union[str, int, float, bool]] = {}
        for key, value in self.key_values():
            parameters[key] = value.get_value()
        return parameters
