from PyQt5.QtCore import *  # QSize

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from PyQt5.QtWidgets import *  # QMainWindow

from src.framework.graph import *
from src.viewer.items import *


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, window: QMainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        self._main = window
        self._grid = self.init_grid()
        self._is_grid = True
        self.set_grid(self._is_grid)
        self._axes = dict()
        self._edges = dict()

    # public methods
    def is_grid(self):
        return self._is_grid

    def set_grid(self, is_grid):
        self._is_grid = is_grid
        if is_grid and self._grid not in self.items:
            self.addItem(self._grid)
            print('Grid enabled')
        elif not is_grid and self._grid in self.items:
            self.removeItem(self._grid)
            print('Grid disabled')

    # initialisers
    def init_grid(self):
        grid = gl.GLGridItem(color=qtg.mkColor((255, 255, 255, 40)))
        grid.setSize(100, 100)
        grid.setSpacing(1, 1)
        return grid

    # helper-methods
    def add_graph(self, graph: Graph):
        axes = Axes(graph)
        self._axes[graph.get_id()] = axes
        self.addItem(axes)
        edges = Edges(graph)
        self._edges[graph.get_id()] = edges
        self.addItem(edges)

    def replace_graph(self, old: Graph, graph: Graph):
        self.remove_graph(old)
        self.add_graph(graph)

    def remove_graph(self, graph: Graph):
        axes = self._axes[graph.get_id()]
        self.removeItem(axes)
        edges = self._edges[graph.get_id()]
        self.removeItem(edges)
