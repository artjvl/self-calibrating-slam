import typing as tp

from src.framework.graph.data.Data import Data
from src.framework.graph.data.Parser import Parser
from src.framework.math.matrix.square import SubSquare, Square3, Square2

SubDataSquare = tp.TypeVar('SubDataSquare', bound='DataSquare', covariant=True)


class DataSquare(Data[SubSquare]):
    _type: tp.Type[SubSquare]

    def __init__(
            self,
            value: tp.Optional[SubSquare] = None
    ):
        super().__init__(value)
        self._size = self._type.get_dimension()

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubSquare = Parser.list_to_symmetric(floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = Parser.symmetric_to_list(self.get_value())
        return Parser.list_to_words(floats)

    @classmethod
    def get_length(cls) -> int:
        dim: int = cls._type.get_dimension()
        return int((dim + 1) * dim / 2)


class DataSquare2(DataSquare):
    _type = Square2


class DataSquare3(DataSquare):
    _type = Square3
