import numpy as np
from typing import *

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
        self._graphs: Dict[int, Graph] = dict()
        self._points: Dict[int, Dict[Type[FactorNode], Points]] = dict()
        self._axes: Dict[int, Dict[Type[FactorNode], Axes]] = dict()
        self._edges: Dict[int, Dict[Type[FactorEdge], Edges]] = dict()
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
        for id, graph in self._graphs.items():
            if id in self._points:
                for points in self._points[id].values():
                    items.append(points)
            if id in self._axes:
                for axes in self._axes[id].values():
                    items.append(axes)
            if id in self._edges:
                for edges in self._edges[id].values():
                    items.append(edges)

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
        id = graph.get_id()
        self._graphs[id] = graph
        for node_type in graph.get_node_types():
            nodes = graph.get_nodes_of_type(node_type)

            # points
            points = Points([node.get_point3() for node in nodes])
            self._points[id] = dict()
            self._points[id][node_type] = points

            # axes
            if node_type.has_rotation:
                axes = Axes([node.get_pose3() for node in nodes])
                self._axes[id] = dict()
                self._axes[id][node_type] = axes

        # edges
        for edge_type in graph.get_edge_types():
            edges = graph.get_edges_of_type(edge_type)
            points = Edges([edge.get_endpoints3() for edge in edges])
            self._edges[id] = dict()
            self._edges[id][edge_type] = points

        self.update_items()

    def replace_graph(self, old: Graph, graph: Graph):
        self.remove_graph(old)
        self.add_graph(graph)
        self.update_items()

    def remove_graph(self, graph: Graph):
        id = graph.get_id()
        self._graphs.pop(id)
        self._points.pop(id)
        self._axes.pop(id)
        self._edges.pop(id)
        self.update_items()

    # PyQtGraph override:
    def pan(self, dx, dy, dz, relative='global'):
        if relative == 'view-upright':
            camera_pos = self.cameraPosition()
            camera_vector = self.opts['center'] - camera_pos
            distance = camera_vector.length()  # distance from camera to center
            distance_x = distance * 2. * np.tan(0.5 * self.opts['fov'] * np.pi / 180.)  # approx. width of view at distance of center point
            scale_x = distance_x / self.width()
            z = QVector3D(0, 0, 1)
            azimuth = np.radians(self.opts['azimuth'])
            x = QVector3D(np.sin(azimuth), -np.cos(azimuth), 0)
            y = np.sign(self.opts['elevation']) * QVector3D.crossProduct(x, z).normalized()
            self.opts['center'] = self.opts['center'] + x * scale_x * dx + y * scale_x * dy + z * scale_x * dz
            self.update()
        else:
            super().pan(dx, dy, dz, relative)
