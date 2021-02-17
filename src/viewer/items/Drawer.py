from OpenGL.GL import *
from typing import *

from src.framework.structures import *
from src.framework.groups import *
from src.viewer.colours import *


class Drawer(object):

    @staticmethod
    def axis(pose: SE3, size: Optional[float] = 0.2):
        centre = pose.translation()
        matrix = pose.rotation().matrix()
        units = [Vector([1, 0, 0]),
                 Vector([0, 1, 0]),
                 Vector([0, 0, 1])]
        x = size * Vector(matrix @ units[0])
        y = size * Vector(matrix @ units[1])
        z = size * Vector(matrix @ units[2])

        alpha = .6

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
    def line(a: Vector, b: Vector, colour: Optional[Colour] = Colours.WHITE):
        glColor4f(*(colour.value.tuple()))
        glVertex3f(*(a.to_list()))
        glVertex3f(*(b.to_list()))

    @staticmethod
    def point(point: Vector, colour: Optional[Colour] = Colours.WHITE):

        glColor4f(*(colour.value.tuple()))
        glVertex3f(*(point.to_list()))
