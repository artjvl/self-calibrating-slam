import numpy as np

from src.framework.structures import *
from src.framework.groups.SO import SO


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

    def quaternion(self):
        m = self.matrix()
        if m[2][2] < 0:                 # is |(x, y)| bigger than |(z, w)|?
            if m[0][0] > m[1][1]:       # is |x| bigger than |y|?
                t = 1 + m[0][0] - m[1][1] - m[2][2]
                quaternion = Quaternion(w=m[2][1] - m[1][2], x=t, y=m[1][0] + m[0][1], z=m[0][2] + m[2][0])
            else:                       # is |y| bigger than |x|?
                t = 1 - m[0][0] + m[1][1] - m[2][2]
                quaternion = Quaternion(w=m[0][2] - m[2][0], x=m[1][0] + m[0][1], y=t, z=m[2][1] + m[1][2])
        else:                           # is |(z, w)| bigger than |(x, y)|?
            if m[0][0] < - m[1][1]:     # is |z| bigger than |w|?
                t = 1 - m[0][0] - m[1][1] + m[2][2]
                quaternion = Quaternion(w=m[1][0] - m[0][1], x=m[0][2] + m[2][0], y=m[2][1] + m[1][2], z=t)
            else:                       # is |w| bigger than |z|?
                t = 1 + m[0][0] + m[1][1] + m[2][2]
                quaternion = Quaternion(w=t, x=m[2][1] - m[1][2], y=m[0][2] - m[2][0], z=m[1][0] - m[0][1])
        return (0.5 / np.sqrt(t)) * quaternion

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

            # matrix = np.eye(3) + (np.sin(angle)/angle) * algebra + \
            #     ((1 - np.cos(angle))/(angle**2)) * (algebra @ algebra)

            matrix = np.eye(3) + np.sin(angle) * unit_algebra + \
                (1 - np.cos(angle)) * (unit_algebra @ unit_algebra)
        return cls(Square(matrix))

    @classmethod
    def from_elements(cls, r1, r2, r3):
        vector = Vector([r1, r2, r3])
        return cls.from_vector(vector)

    @classmethod
    def from_quaternion(cls, quaternion):
        assert isinstance(quaternion, Quaternion)
        w = quaternion.w()
        x = quaternion.x()
        y = quaternion.y()
        z = quaternion.z()
        matrix = [[1 - 2 * (y ** 2 + z ** 2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                  [2 * (x * y + z * w), 1 - 2 * (x ** 2 + z ** 2), 2 * (y * z - x * w)],
                  [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x ** 2 + y ** 2)]]
        return cls.from_matrix(matrix)

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
