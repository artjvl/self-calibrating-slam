import typing as tp

from src.framework.graph.data.Data import Data
from src.framework.graph.data.Parser import Parser
from src.framework.math.matrix.vector import SubVector, Vector2, Vector3, Vector6

SubDataVector = tp.TypeVar('SubDataVector', bound='DataVector', covariant=True)


class DataVector(Data[SubVector]):
    _type: tp.Type[SubVector]

    def __init__(
            self,
            value: tp.Optional[SubVector] = None
    ):
        super().__init__(value)
        self._size = self._type.get_dim()

    def to_vector(self) -> SubVector:
        return self.get_value()

    def from_vector(self, vector: SubVector) -> None:
        assert vector.get_dim() == self.get_dim()
        self.set_value(vector)

    def read(self, words: tp.List[str]) -> None:
        floats: tp.List[float] = Parser.words_to_list(words)
        value: SubVector = self._type(floats)
        self.set_value(value)

    def write(self) -> tp.List[str]:
        floats: tp.List[float] = self.get_value().to_list()
        return Parser.list_to_words(floats)

    def oplus(self, delta: SubVector) -> SubVector:
        assert self.has_value()
        assert delta.get_dim() == self.get_dim()
        return self._type(self.get_value().array() + delta.array())

    @classmethod
    def get_dim(cls) -> int:
        return cls._type.get_dim()


class DataV2(DataVector):
    _type = Vector2


class DataV3(DataVector):
    _type = Vector3


class DataV6(DataVector):
    _type = Vector6
