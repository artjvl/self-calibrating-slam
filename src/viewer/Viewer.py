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
        self._is_axes = True
        self._is_edges = True
        self._axes = dict()
        self._edges = dict()
        self.set_grid(self._is_grid)

    # public methods
    def is_empty(self):
        return not (self._axes and self._edges)

    def is_grid(self):
        return self._is_grid

    def is_axes(self):
        return self._is_axes

    def is_edges(self):
        return self._is_edges

    def set_grid(self, is_grid):
        self._is_grid = is_grid
        self.update_items()

    def set_axes(self, is_axes):
        self._is_axes = is_axes
        self.update_items()

    def set_edges(self, is_edges):
        self._is_edges = is_edges
        self.update_items()

    def update_items(self):
        items = []
        if self.is_grid():
            items.append(self._grid)
        if self.is_axes():
            items.extend(self._axes.values())
        if self.is_edges():
            items.extend(self._edges.values())
        for item in self.items:
            item._setView(None)
        for item in items:
            item._setView(self)
        self.items = items
        self.update()

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
        edges = Edges(graph)
        self._edges[graph.get_id()] = edges
        self.update_items()

    def replace_graph(self, old: Graph, graph: Graph):
        self.remove_graph(old)
        self.add_graph(graph)
        self.update_items()

    def remove_graph(self, graph: Graph):
        self._axes.pop(graph.get_id())
        self._edges.pop(graph.get_id())
        self.update_items()
