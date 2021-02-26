from typing import *

from OpenGL.GL import *

from src.framework.groups import SE3
from src.framework.structures import Vector
from src.gui.viewer.Colour import Colour


class Drawer(object):

    @staticmethod
    def axis(pose: SE3, size: Optional[float] = 0.2, alpha: float = 0.5):
        centre = pose.translation()
        matrix = pose.rotation().matrix()
        units = [Vector([1, 0, 0]),
                 Vector([0, 1, 0]),
                 Vector([0, 0, 1])]
        x = size * Vector(matrix @ units[0])
        y = size * Vector(matrix @ units[1])
        z = size * Vector(matrix @ units[2])

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
    def line(a: Vector, b: Vector, colour: Optional[Tuple[float, ...]] = Colour.WHITE, alpha: float = 0.5):
        glColor4f(*colour, alpha)
        glVertex3f(*(a.to_list()))
        glVertex3f(*(b.to_list()))

    @staticmethod
    def point(point: Vector, colour: Optional[Tuple[float, ...]] = Colour.WHITE, alpha: float = 0.5):
        glColor4f(*colour, alpha)
        glVertex3f(*(point.to_list()))
