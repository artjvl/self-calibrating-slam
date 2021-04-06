import typing as tp

from src.framework.graph.FactorGraph import FactorNode
from src.framework.graph.data import SubData
from src.framework.graph.data.DataFactory import Supported, DataFactory

SubCalibratingNode = tp.TypeVar('SubCalibratingNode', bound='CalibratingNode')


class CalibratingNode(FactorNode):

    _type: tp.Type[SubData]

    def __init__(
            self,
            id_: int = 0,
            value: tp.Optional[Supported] = None
    ):
        super().__init__(id_)
        self._value: SubData = DataFactory.from_type(self.get_type())(value)

    # interface
    def get_value(self) -> Supported:
        assert self._value.has_value()
        return self._value.get_value()

    @classmethod
    def get_type(cls) -> tp.Type[Supported]:
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
