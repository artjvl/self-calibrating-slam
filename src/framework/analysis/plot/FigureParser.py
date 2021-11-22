import pathlib
import pickle as pkl
import typing as tp
from datetime import datetime

from matplotlib import pyplot as plt
from src.definitions import get_project_root


class FigureParser(object):
    _path: pathlib.Path = (get_project_root() / 'plots').resolve()

    @classmethod
    def path(cls) -> pathlib.Path:
        return cls._path

    @classmethod
    def save(
            cls,
            fig: plt.Figure,
            name: tp.Optional[str] = None
    ) -> None:
        if name is None:
            name = f"pickle_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        if not name.endswith('.pickle'):
            name += '.pickle'
        cls._path.mkdir(parents=True, exist_ok=True)
        path: pathlib.Path = (cls._path / name).resolve()
        with open(path, 'wb') as file:
            pkl.dump(fig, file)
        print(f"src/FigureParser: Figure saved as {path}")

    @classmethod
    def load(
            cls,
            name: str
    ) -> plt.Figure:
        if not name.endswith('.pickle'):
            name += '.pickle'
        path: pathlib.Path = (cls._path / name).resolve()
        assert path.is_file()
        with open(path, 'rb') as file:
            fig: plt.Figure = pkl.load(file)
        dummy = plt.figure()
        new_manager = dummy.canvas.manager
        new_manager.canvas.figure = fig
        fig.set_canvas(new_manager.canvas)
        return fig