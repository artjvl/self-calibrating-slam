import typing as tp

from src.framework.graph.data.Data import Data
from src.framework.graph.data.Parser import Parser
from src.framework.math.lie.transformation import SE2
from src.framework.math.lie.transformation.SE import SubSE
from src.framework.math.matrix.vector import SubVector
from src.framework.math.matrix.vector import Vector3

SubDataSE = tp.TypeVar('SubDataSE', bound='DataSE', covariant=True)


class DataSE(Data[SubSE]):
    _type: tp.Type[SubSE]

    def __init__(
            self,
            value: tp.Optional[SubSE] = None
    ):
        super().__init__(value)

    def to_vector(self) -> SubVector:
        return self.get_value().vector()

    def from_vector(self, vector: SubVector) -> None:
        assert vector.get_dim() == self.get_dim()
        self.set_value(self.get_type().from_vector(vector))

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubSE = self._type.from_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = self.get_value().vector().to_list()
        return Parser.list_to_words(floats)

    def oplus(self, delta: SubVector) -> SubSE:
        assert self.has_value()
        assert delta.get_dim() == self.get_dim()
        return self.get_value().oplus(delta)

    @classmethod
    def get_dim(cls) -> int:
        return cls._type.get_dof()


class DataSE2(DataSE):
    _type = SE2

    def to_vector(self) -> Vector3:
        return self.get_value().translation_angle_vector()

    def from_vector(self, vector: SubVector) -> None:
        assert vector.get_dim() == self.get_dim()
        self.set_value(self.get_type().from_translation_angle_vector(vector))

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubSE = self._type.from_translation_angle_elements(*floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = self.get_value().translation_angle_list()
        return Parser.list_to_words(floats)