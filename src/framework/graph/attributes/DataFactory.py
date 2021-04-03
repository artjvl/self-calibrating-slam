import typing as tp

from src.framework.graph.attributes.Data import Data, SubData
from src.framework.graph.attributes.Parser import Parser
from src.framework.groups import SE2
from src.framework.structures import Vector2, Vector3, Square

Supported = tp.Union[SE2, Vector2, Vector3, Square]


class DataSE2(Data[SE2]):
    _dimension = 3

    def __init__(
            self,
            value: tp.Optional[SE2] = None
    ):
        super().__init__(SE2, value)

    def read(self, words: tp.List[str]):
        floats: tp.List[float] = [float(word) for word in words]
        value: SE2 = SE2.from_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        lst = self.get_value().vector().to_list()
        return Parser.list_to_words(lst)


class DataV2(Data[Vector2]):
    _dimension = 2

    def __init__(
            self,
            value: tp.Optional[Vector2] = None
    ):
        super().__init__(Vector2, value)

    def read(self, words: tp.List[str]):
        floats: tp.List[float] = [float(word) for word in words]
        value: Vector2 = Vector2.from_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        lst = self.get_value().to_list()
        return Parser.list_to_words(lst)


class DataV3(Data[Vector3]):
    _dimension = 3

    def __init__(
            self,
            value: tp.Optional[Vector2] = None
    ):
        super().__init__(Vector2, value)

    def read(self, words: tp.List[str]):
        floats: tp.List[float] = [float(word) for word in words]
        value: Vector3 = Vector3.from_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        lst = self.get_value().to_list()
        return Parser.list_to_words(lst)


class DataSquare(Data[Square]):
    _dimension = 6

    def __init__(
            self,
            value: tp.Optional[Square] = None
    ):
        super().__init__(Square, value)

    def read(self, words: tp.List[str]):
        floats: tp.List[float] = [float(word) for word in words]
        value: Square = Parser.list_to_symmetric(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        lst: tp.List[float] = Parser.symmetric_to_list(self.get_value())
        return Parser.list_to_words(lst)


class DataFactory(object):
    _map: tp.Dict[tp.Type[Supported], tp.Type[SubData]] = {
        SE2: DataSE2,
        Vector2: DataV2,
        Vector3: DataV3,
        Square: DataSquare
    }

    @classmethod
    def from_type(cls, type_: tp.Type[Supported]) -> tp.Type[SubData]:
        assert type_ in cls._map, f'Type {type_} not supported.'
        return cls._map[type_]

    @classmethod
    def from_value(cls, value: Supported) -> SubData:
        return cls.from_type(type(value))(value)
