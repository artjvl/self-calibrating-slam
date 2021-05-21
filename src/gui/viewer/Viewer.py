import numpy as np
import pyqtgraph.opengl as gl
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QVector3D

from src.framework.math.matrix.vector import Vector3
from src.gui.modules.Container import TopContainer
from src.gui.viewer.Grid import Grid


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, container: TopContainer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        self.set_isometric_view()
        self._container: TopContainer = container
        self._container.signal_update.connect(self.update_items)
        self._is_grid = True
        self._grid = Grid(size=(100, 100), spacing=(1, 1))
        self.update_items()

    # public methods
    def set_top_view(self):
        self.setCameraPosition(elevation=90, azimuth=-90)

    def set_isometric_view(self):
        self.setCameraPosition(elevation=60, azimuth=-120)

    def set_home_view(self):
        self.setCameraPosition(pos=QVector3D(0, 0, 0))
        # self.set_isometric_view()

    def set_camera_pos(self, pos: Vector3):
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

    def focus(self, translation: Vector3):
        self.set_camera_pos(translation)

    def toggle_grid(self):
        self._is_grid = not self._is_grid
        self.update_items()

    # PyQtGraph override:
    def pan(self, dx, dy, dz, relative='global'):
        if relative == 'view-upright':
            camera_pos = self.cameraPosition()
            camera_vector = self.opts['center'] - camera_pos
            distance = camera_vector.length()  # distance from camera to center
            distance_x = distance * 2. * np.tan(0.5 * self.opts['fov'] * np.pi / 180.)
            scale_x = distance_x / self.width()
            z = QVector3D(0, 0, 1)
            azimuth = np.radians(self.opts['azimuth'])
            x = QVector3D(np.sin(azimuth), -np.cos(azimuth), 0)
            y = np.sign(self.opts['elevation']) * QVector3D.crossProduct(x, z).normalized()
            self.opts['center'] = self.opts['center'] + x * scale_x * dx + y * scale_x * dy + z * scale_x * dz
            self.update()
        else:
            super().pan(dx, dy, dz, relative)
