import typing as tp

from src.framework.graph.data.Data import Data
from src.framework.graph.data.Parser import Parser
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SubSE

SubDataSE = tp.TypeVar('SubDataSE', bound='DataSE', covariant=True)


class DataSE(Data[SubSE]):
    _type: tp.Type[SubSE]

    def __init__(
            self,
            value: tp.Optional[SubSE] = None
    ):
        super().__init__(value)

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubSE = self._type.from_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = self.get_value().vector().to_list()
        return Parser.list_to_words(floats)

    @classmethod
    def get_length(cls) -> int:
        return cls._type.get_dof()


class DataSE2(DataSE):
    _type = SE2

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubSE = self._type.from_translation_angle_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = self.get_value().translation_angle_list()
        return Parser.list_to_words(floats)