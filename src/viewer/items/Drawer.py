from OpenGL.GL import *

from framework.structures import *
from framework.groups import *


class Drawer(object):

    @staticmethod
    def axis(pose, size=0.2):
        assert isinstance(pose, SE3)
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
    def line(a, b, colour=(1, 1, 1, 0.6)):
        assert isinstance(a, Vector)
        assert isinstance(b, Vector)

        glColor4f(*colour)
        glVertex3f(*(a.to_list()))
        glVertex3f(*(b.to_list()))
