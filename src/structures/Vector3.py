from .Vector import Vector


class Vector3(Vector):

    # constructor
    def __new__(cls, x, y, z):
        return super(Vector3, cls).__new__(cls, [x, y, z])

    # public methods
    def x(self):
        return self[0][0]

    def y(self):
        return self[1][0]

    def z(self):
        return self[2][0]
