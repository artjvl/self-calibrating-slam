import configparser
import pathlib
import typing as tp

Type = tp.Union[tp.Type[str], tp.Type[int], tp.Type[float], tp.Type[bool]]
Value = tp.Union[str, int, float, bool]


class Parameter(object):

    _prefixes = {
        's_': str,
        'i_': int,
        'f_': float,
        'b_': bool
    }

    # constructor
    def __init__(
            self,
            key: str,
            value: str
    ):
        prefix: str = key[:2]
        assert prefix in self._prefixes, f"Prefix '{prefix}' not found in '{self._prefixes}'"

        self._name: str = key[2:]
        self._type: Type = self._prefixes[prefix]
        self._value: Value = self.parse(value)

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> Value:
        return self._value

    def set_value(self, value: Value):
        self._value = self.parse(value)

    def parse(self, value: Value):
        parsed: tp.Optional[Value] = None
        try:
            parsed = self.get_type()(value)
        except ValueError:
            pass
        assert parsed is not None
        return parsed

    def get_type(self) -> Type:
        return self._type


class ParameterSet(object):

    def __init__(self, path: pathlib.Path):
        config = configparser.ConfigParser()
        config.read(path)
        assert 'PARAMETERS' in config
        dict_: tp.Dict[str, Value] = dict(config['PARAMETERS'])

        self._parameters: tp.Dict[str, Parameter] = {}
        for key, value in dict_.items():
            parameter = Parameter(key, value)
            self._parameters[parameter.get_name()] = parameter

    def __getitem__(self, key: str) -> Value:
        return self._parameters[key].get_value()

    def __setitem__(self, key, value):
        parameter: Parameter = self.get(key)
        parameter.set_value(value)

    def get(self, index: int) -> Parameter:
        return list(self._parameters.values())[index]

    def to_dict(self) -> tp.Dict[str, Parameter]:
        return self._parameters
