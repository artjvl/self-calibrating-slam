import numpy as np

from src.framework.structures.Vector import Vector


class Vector2(Vector):

    # constructor
    def __new__(cls, x, y):
        return super(Vector2, cls).__new__(cls, [x, y])

    # public methods
    def x(self):
        return self[0][0]

    def y(self):
        return self[1][0]

    # open class-methods
    @classmethod
    def from_list(cls, elements):
        assert isinstance(elements, (list, np.ndarray))
        return cls(elements[0], elements[1])
