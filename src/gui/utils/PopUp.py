import pathlib
import typing as tp

from PyQt5 import QtWidgets
from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphParser import GraphParser


class PopUp(object):

    @staticmethod
    def load_from_file() -> tp.Optional[SubGraph]:
        filename: tp.Optional[str]
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            caption='Select file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename:
            path = pathlib.Path(filename)
            graph: SubGraph = GraphParser.load(path, should_sort=True)
            return graph
        return None

    @classmethod
    def load_with_callback(
            cls,
            callback: tp.Callable,
            *args, **kwargs
    ) -> None:
        graph: tp.Optional[SubGraph] = cls.load_from_file()
        if graph is not None:
            try:
                callback(graph, *args, **kwargs)
            finally:
                pass

    @staticmethod
    def save_file(graph: SubGraph) -> None:
        filename: tp.Optional[str]
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption='Save as file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename:
            if not filename.endswith('.g2o'):
                filename += '.g2o'
            GraphParser.save(graph, pathlib.Path(filename))
