import typing as tp

from src.framework.graph.FactorGraph import FactorNode
from src.framework.graph.attributes.DataFactory import Supported
from src.framework.graph.protocols.ContainsData import ContainsData

SubNode = tp.TypeVar('SubNode', bound='CalibratingNode')


class CalibratingNode(FactorNode, ContainsData):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__(id_)

    # interface
    def get_value(self) -> Supported:
        return self.get_data()

    def read(self, words: tp.List[str]) -> None:
        words = self._data.read_rest(words)
        assert not words, f"Words '{words} are left unread."

    def write(self) -> tp.List[str]:
        words: tp.List[str] = self._data.write()
        return words

    def get_word_count(self) -> int:
        return 0
