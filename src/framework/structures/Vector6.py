import numpy as np

from src.framework.structures.Vector import Vector
from src.framework.structures.Vector3 import Vector3


class Vector6(Vector):

    # constructor
    def __new__(cls, x, y, z, a, b, c):
        return super(Vector6, cls).__new__(cls, [x, y, z, a, b, c])

    # public methods
    def x(self):
        return self[0][0]

    def y(self):
        return self[1][0]

    def z(self):
        return self[2][0]

    def a(self):
        return self[3][0]

    def b(self):
        return self[4][0]

    def c(self):
        return self[5][0]

    def split(self):
        return Vector3.from_list(self[0:3]), Vector3.from_list(self[3:6])

    # open class-methods
    @classmethod
    def from_list(cls, elements):
        assert isinstance(elements, (list, np.ndarray))
        return cls(elements[0], elements[1], elements[2], elements[3], elements[4], elements[5])
