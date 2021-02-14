import numpy as np

from PyQt5.QtCore import *  # QSize
from PyQt5.QtWidgets import *  # QMainWindow
from PyQt5.QtGui import *

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from src.framework.structures import *
from src.framework.graph import *
from src.viewer.items import *


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, window: QMainWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        self.set_isometric_view()
        self._main = window
        self._grid = self.init_grid()
        self._is_grid = True
        self._is_axes = False
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

    def set_top_view(self):
        self.setCameraPosition(elevation=90, azimuth=-90)

    def set_isometric_view(self):
        self.setCameraPosition(elevation=60, azimuth=-120)

    def set_home_view(self):
        self.setCameraPosition(pos=QVector3D(0, 0, 0))
        # self.set_isometric_view()

    def set_camera_pos(self, pos: Vector):
        self.setCameraPosition(pos=QVector3D(*(pos.to_list())))

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

    def focus(self, element: FactorNode):
        self._main.viewer.set_camera_pos(element.get_point3())

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

    # PyQtGraph override:
    def pan(self, dx, dy, dz, relative='global'):
        if relative == 'view-upright':
            cPos = self.cameraPosition()
            cVec = self.opts['center'] - cPos
            dist = cVec.length()  ## distance from camera to center
            xDist = dist * 2. * np.tan(0.5 * self.opts['fov'] * np.pi / 180.)  ## approx. width of view at distance of center point
            xScale = xDist / self.width()
            zVec = QVector3D(0, 0, 1)
            azimuth = np.radians(self.opts['azimuth'])
            xVec = QVector3D(np.sin(azimuth), -np.cos(azimuth), 0)
            yVec = np.sign(self.opts['elevation']) * QVector3D.crossProduct(xVec, zVec).normalized()
            self.opts['center'] = self.opts['center'] + xVec * xScale * dx + yVec * xScale * dy + zVec * xScale * dz
            self.update()
        else:
            super().pan(dx, dy, dz, relative)
