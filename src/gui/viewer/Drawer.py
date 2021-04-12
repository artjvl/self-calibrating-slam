import typing as tp

import numpy as np
from OpenGL.GL import *

from src.framework.math.lie.rotation import SO3
from src.framework.math.lie.transformation import SE3
from src.framework.math.matrix.vector import Vector3
from src.gui.viewer.Rgb import Rgb, RgbTuple


class Drawer(object):

    @staticmethod
    def axis(
            pose: SE3,
            size: float = 0.2,
            alpha: float = 0.5
    ):
        centre: np.ndarray = pose.translation().array()
        rotation: np.ndarray = pose.rotation().array()
        units: tp.List[Vector3] = [
            Vector3(1, 0, 0),
            Vector3(0, 1, 0),
            Vector3(0, 0, 1)
        ]
        x: np.ndarray = size * (rotation @ units[0].array())
        y: np.ndarray = size * (rotation @ units[1].array())
        z: np.ndarray = size * (rotation @ units[2].array())

        glColor4f(1, 0, 0, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + x))

        glColor4f(0, 1, 0, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + y))

        glColor4f(0, 0, 1, alpha)
        glVertex3f(*centre)
        glVertex3f(*(centre + z))

    @staticmethod
    def line(
            a: Vector3,
            b: Vector3,
            colour: RgbTuple = Rgb.WHITE,
            alpha: float = 0.5
    ) -> None:
        glColor4f(*colour, alpha)
        glVertex3f(*(a.to_list()))
        glVertex3f(*(b.to_list()))

    @staticmethod
    def point(
            point: Vector3,
            colour: RgbTuple = Rgb.WHITE,
            alpha: float = 0.5
    ) -> None:
        glColor4f(*colour, alpha)
        glVertex3f(*(point.to_list()))
