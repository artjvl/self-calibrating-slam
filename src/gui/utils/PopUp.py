import pathlib
import typing as tp

from PyQt5 import QtWidgets
from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphParser import GraphParser


class PopUp(object):

    @staticmethod
    def load_from_file() -> tp.Optional[tp.Tuple[SubGraph, pathlib.Path]]:
        filename: tp.Optional[str]
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            caption='Select file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename:
            path = pathlib.Path(filename)
            graph: SubGraph = GraphParser.load(path, should_sort=True)
            return graph, path
        return None

    @classmethod
    def load_with_callback(
            cls,
            callback: tp.Callable,
            *args, **kwargs
    ) -> None:
        load: tp.Optional[tp.Tuple[SubGraph, pathlib.Path]] = PopUp.load_from_file()
        if load is not None:
            graph: SubGraph
            path: pathlib.Path
            graph, path = load
            try:
                callback(graph, *args, **kwargs)
            finally:
                pass

    @staticmethod
    def save_file(graph: SubGraph) -> tp.Optional[pathlib.Path]:
        filename: tp.Optional[str]
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption='Save as file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename:
            if not filename.endswith('.g2o'):
                filename += '.g2o'
            path: pathlib.Path = pathlib.Path(filename)
            GraphParser.save(graph, path)
            return path
        return None
