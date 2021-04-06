import typing as tp

from src.framework.graph.FactorGraph import FactorNode
from src.framework.graph.data import SubData
from src.framework.graph.data.DataFactory import DataFactory

SubCalibratingNode = tp.TypeVar('SubCalibratingNode', bound='CalibratingNode')
T = tp.TypeVar('T')


class CalibratingNode(tp.Generic[T], FactorNode[T]):
    _type: tp.Type[T]

    def __init__(
            self,
            id_: int = 0,
            value: tp.Optional[T] = None
    ):
        super().__init__(id_)
        self._value: SubData = DataFactory.from_type(self.get_type())(value)

    # interface
    def get_value(self) -> T:
        assert self._value.has_value()
        return self._value.get_value()

    @classmethod
    def get_type(cls) -> tp.Type[T]:
        return cls._type

    # read/write
    def read(self, words: tp.List[str]) -> None:
        words = self._value.read_rest(words)
        assert not words, f"Words '{words} are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._value.write()
        return words

    @classmethod
    def get_length(cls) -> int:
        return cls.get_type().get_length()
