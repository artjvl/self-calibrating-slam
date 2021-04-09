import typing as tp

from src.framework.graph.FactorGraph import FactorGraph

SubGraph = tp.TypeVar('SubGraph', bound='Graph')


class Graph(FactorGraph):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__()
        self._id = id_

    def get_id(self) -> int:
        return self._id

    def set_id(self, id_: int) -> None:
        self._id = id_
