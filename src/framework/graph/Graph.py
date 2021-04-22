import pathlib
import typing as tp
from datetime import datetime

from src.framework.graph.FactorGraph import FactorGraph

SubGraph = tp.TypeVar('SubGraph', bound='Graph')


class Graph(FactorGraph):

    def __init__(
            self,
            id_: int = 0
    ):
        super().__init__()
        self._id: int = id_

        self._date: str = datetime.now().strftime('%Y%m%d-%H%M%S')
        self._path: tp.Optional[pathlib.Path] = None
        self._suffix: tp.Optional[str] = None

    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def get_path(self) -> pathlib.Path:
        return self._path

    def get_pathname(self) -> str:
        return self._path.name

    def get_id(self) -> int:
        return self._id

    def set_id(self, id_: int) -> None:
        self._id = id_
