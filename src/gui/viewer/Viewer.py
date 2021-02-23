import numpy as np
import pyqtgraph as qtg
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QVector3D

from src.framework.structures import Vector
from src.gui.GraphContainer import GraphContainer


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, container: GraphContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        self.set_isometric_view()
        self._container: GraphContainer = container
        self._container.signal_update.connect(self.update_items)
        self._is_grid = True
        self._grid = self.init_grid()
        self.update_items()

    # public methods
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
        items = self._container.get_graphics()
        if self._is_grid:
            items.append(self._grid)

        for item in self.items:
            item._setView(None)
        for item in items:
            item._setView(self)
        self.items = items
        self.update()

    def focus(self, translation: Vector):
        self.set_camera_pos(translation)

    def toggle_grid(self):
        self._is_grid = not self._is_grid
        self.update_items()

    # initialisers
    def init_grid(self):
        grid = gl.GLGridItem(color=qtg.mkColor((255, 255, 255, 40)))
        grid.setSize(100, 100)
        grid.setSpacing(1, 1)
        return grid

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
