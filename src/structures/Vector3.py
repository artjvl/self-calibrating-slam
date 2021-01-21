import numpy as np
from src.structures.Vector import Vector


class Vector3(Vector):

    # constructor
    def __new__(cls, x, y, z):
        return super(Vector3, cls).__new__(cls, [x, y, z])

    # operators
    def __xor__(self, other):
        return np.cross(self, other)

    # public methods
    def x(self):
        return self[0][0]

    def y(self):
        return self[1][0]

    def z(self):
        return self[2][0]

    # open class-methods
    @classmethod
    def from_elements(cls, elements):
        assert len(elements) <= 3
        return cls(elements[0], elements[1], elements[2])
