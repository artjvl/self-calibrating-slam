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
        return type(self).algebra_to_vector(algebra)

    def jacobian(self):
        vector = self.vector()
        algebra = type(self).vector_to_algebra(vector)
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix = np.eye(3) + 0.5 * algebra
        else:
            unit_algebra = algebra / angle

            # unit = vector / angle
            # matrix_ = (np.sin(angle) / angle) * np.eye(3) + \
            #     (1 - np.sin(angle) / angle) * np.outer(unit, unit) + \
            #     ((1 - np.cos(angle)) / angle) * unit_algebra

            matrix = np.eye(3) + ((1 - np.cos(angle)) / angle) * unit_algebra + \
                (1 - np.sin(angle) / angle) * (unit_algebra @ unit_algebra)
        return Square(matrix)

    def inverse_jacobian(self):
        vector = self.vector()
        algebra = type(self).vector_to_algebra(vector)
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix = np.eye(3) + 0.5 * algebra
        else:
            unit_algebra = algebra / angle
            matrix = np.eye(3) - 0.5 * algebra + \
                (1 - 0.5 * angle * np.sin(angle) / (1 - np.cos(angle))) * (unit_algebra @ unit_algebra)
        return Square(matrix)

    @classmethod
    def from_vector(cls, vector):
        assert isinstance(vector, Vector)
        algebra = cls.vector_to_algebra(vector)
        angle = vector.magnitude()
        if np.isclose(angle, 0.):
            matrix = np.eye(3) + algebra
        else:
            unit_algebra = algebra / angle

            # matrix = np.cos(angle) * np.eye(3) + np.sin(angle) * unit_algebra + \
            #     (1 - np.cos(angle)) * np.outer(unit, unit)

            # algebra = cls.vector_to_algebra(vector)
            # matrix = np.eye(3) + (np.sin(angle)/angle) * algebra + \
            #     ((1 - np.cos(angle))/(angle**2)) * (algebra @ algebra)

            matrix = np.eye(3) + np.sin(angle) * unit_algebra + \
                (1 - np.cos(angle)) * (unit_algebra @ unit_algebra)
        return cls(Square(matrix))

    @classmethod
    def from_elements(cls, r1, r2, r3):
        vector = Vector([r1, r2, r3])
        return cls.from_vector(vector)

    @staticmethod
    def vector_to_algebra(vector):
        assert isinstance(vector, Vector)
        a = vector.get(0)
        b = vector.get(1)
        c = vector.get(2)
        return Square([[0, -c, b],
                       [c, 0, -a],
                       [-b, a, 0]])

    @staticmethod
    def algebra_to_vector(algebra):
        assert isinstance(algebra, Square)
        return Vector([algebra[2][1],
                       algebra[0][2],
                       algebra[1][0]])
