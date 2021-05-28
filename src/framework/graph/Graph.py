import pathlib
import typing as tp
from datetime import datetime

from src.framework.graph.FactorGraph import FactorGraph

SubGraph = tp.TypeVar('SubGraph', bound='Graph')


class Graph(FactorGraph):

    def __init__(self):
        super().__init__()

        self._date: str = datetime.now().strftime('%Y%m%d-%H%M%S')
        self._path: tp.Optional[pathlib.Path] = None
        self._suffix: tp.Optional[str] = None

        self._error: tp.Optional[float] = None
        self._ate: tp.Optional[float] = None
        self._rpe_translation: tp.Optional[float] = None
        self._rpe_rotation: tp.Optional[float] = None

    # errors
    def compute_error(self) -> float:
        if self._error is None:
            self._error = super().compute_error()
        return self._error

    def compute_ate(self) -> float:
        if self._ate is None:
            self._ate = super().compute_ate()
        return self._ate

    def compute_rpe_translation(self) -> float:
        if self._rpe_translation is None:
            self._rpe_translation = super().compute_rpe_translation()
        return self._rpe_translation

    def compute_rpe_rotation(self) -> float:
        if self._rpe_rotation is None:
            self._rpe_rotation = super().compute_rpe_rotation()
        return self._rpe_rotation

    # properties
    def set_path(self, path: pathlib.Path) -> None:
        self._path = path

    def get_path(self) -> pathlib.Path:
        return self._path

    def get_pathname(self) -> str:
        return self._path.name

