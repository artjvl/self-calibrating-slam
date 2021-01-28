import numpy as np

from src.framework.structures.Vector import Vector


class Quaternion(Vector):

    # constructor
    def __new__(cls, w, x, y, z):
        return super(Vector, cls).__new__(cls, [w, x, y, z])

    # public methods
    def w(self):
        return self[0][0]

    def x(self):
        return self[1][0]

    def y(self):
        return self[2][0]

    def z(self):
        return self[3][0]

    # public class-methods
    @classmethod
    def from_list(cls, elements):
        assert isinstance(elements, (list, np.ndarray))
        return cls(elements[0], elements[1], elements[2], elements[3])
