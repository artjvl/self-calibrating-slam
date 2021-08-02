import pathlib
import typing as tp

from PyQt5 import QtWidgets
from src.framework.graph.Graph import SubGraph
from src.framework.graph.GraphParser import GraphParser


class PopUp(object):

    @staticmethod
    def load_from_file() -> tp.Optional[SubGraph]:
        filename: tp.Optional[tp.Tuple[str, str]] = QtWidgets.QFileDialog.getOpenFileName(
            caption='Select file',
            directory='',
            filter='g2o (*.g2o)'
        )
        if filename[0]:
            path = pathlib.Path(filename[0])
            graph: SubGraph = GraphParser.load(path)
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
