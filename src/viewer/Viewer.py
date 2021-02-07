from PyQt5.QtCore import *  # QSize

import pyqtgraph.opengl as gl

from src.framework.graph import *
from src.viewer.items import *


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        # self.addItem(self.construct_axis())
        self._graphs = []

    def add_graph(self, graph):
        assert isinstance(graph, Graph)
        self._graphs.append(graph)
        self.addItem(Axes(graph))
        self.addItem(Edges(graph))
