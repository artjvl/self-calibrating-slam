import numpy as np

from PyQt5.QtCore import *  # QSize

import pyqtgraph.opengl as gl
import pyqtgraph as qtg

from framework.structures import *
from framework.groups import *


class Viewer(gl.GLViewWidget):
    # reference: https://pyqtgraph.readthedocs.io/en/latest/

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(QSize(600, 400))
        self.setCameraPosition(distance=40)
        self.addItem(self.construct_axis())

    # helper-methods
    @staticmethod
    def construct_axis(transformation=None) -> gl.GLAxisItem:
        if transformation is None:
            transformation = SE3.from_elements(0, 0, 0, 0, 0, 0)
        else:
            assert isinstance(transformation, SE)
            if isinstance(transformation, SE2):
                transformation = transformation.to_se3()
            assert isinstance(transformation, SE3)
        translation = transformation.translation()
        rotation = transformation.rotation()
        vector = rotation.vector()
        angle = rotation.angle()
        axis = gl.GLAxisItem()
        axis.rotate(angle * 180/np.pi, vector.get(0), vector.get(1), vector.get(2))
        axis.translate(translation.get(0), translation.get(1), translation.get(2))
        return axis

    @staticmethod
    def line(a, b, color=None):
        assert isinstance(a, Vector)
        assert isinstance(b, Vector)
        pos = np.vstack(a.reshape((1, -1)), b.reshape((1, -1)))
        line = gl.GLLinePlotItem(pos=pos, width=2)
        return line
