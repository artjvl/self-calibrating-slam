import numpy as np

from src.structures import *
from src.groups.SO import SO


class SO3(SO):

    # static properties
    _dim = 3
    _dof = 3

    # constructor
    def __init__(self, matrix):
        assert isinstance(matrix, Square)
        super().__init__(matrix)

    # public methods
    def angle(self):
        return self.vector().magnitude()

    # abstract implementations
    def vector(self):
        matrix = self.matrix()
        angle = np.arccos(0.5 * (np.trace(matrix) - 1))
        if np.isclose(angle, 0.):
            algebra = matrix - np.eye(3)
        else:
            algebra = (angle * (matrix - np.transpose(matrix))) / (2 * np.sin(angle))
        return Vector([algebra[2][1],
                       algebra[0][2],
                       algebra[1][0]])

    def jacobian(self):
        vector = self.vector()
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix = np.eye(3) + 0.5 * type(self).vector_to_algebra(vector)
        else:
            unit = vector.normal()
            unit_algebra = type(self).vector_to_algebra(unit)
            matrix = np.eye(3) + (1 - np.cos(angle)) * unit_algebra + (1 - np.sin(angle) / angle) * unit_algebra**2
        return Square(matrix)

    def inverse_jacobian(self):
        vector = self.vector()
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix = np.eye(3) + 0.5 * type(self).vector_to_algebra(vector)
        else:
            unit = vector.normal()
            unit_algebra = type(self).vector_to_algebra(unit)
            matrix = np.eye(3) - 0.5 * angle * unit_algebra + \
                (1 - 0.5 * angle * (np.sin(angle) / (1 - np.cos(angle)))) * unit_algebra**2
        return Square(matrix)

    @classmethod
    def from_vector(cls, vector):
        assert isinstance(vector, Vector)
        angle = vector.magnitude()
        unit = vector.normal()
        unit_algebra = cls.vector_to_algebra(unit)

        # Rodrigues formula
        matrix = np.eye(3) + unit_algebra*np.sin(angle) + (unit_algebra**2)*(1 - np.cos(angle))
        return cls(Square(matrix))

    @classmethod
    def from_elements(cls, r1, r2, r3):
        vector = Vector([r1, r2, r3])
        return cls.from_vector(vector)

    @staticmethod
    def elements():
        return list([Square([[0, 0, 0], [0, 0, -1], [0, 1, 0]]),
                     Square([[0, 0, 1], [0, 0, 0], [-1, 0, 0]]),
                     Square([[0, -1, 0], [1, 0, 0], [0, 0, 0]])])
