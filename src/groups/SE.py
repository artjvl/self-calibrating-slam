from abc import ABC, abstractmethod
from src.structures import *
from src.groups.Group import Group
from src.groups.SO3 import SO3


class SE(Group, ABC):

    # constructor
    def __init__(self, translation, rotation):
        assert isinstance(translation, Vector)
        assert isinstance(rotation, SO)
        vector = Vector(np.vstack((translation, rotation.vector())))
        super().__init__(vector)
        self._translation = translation
        self._rotation = rotation

    # public methods
    def translation(self):
        return self._translation

    def rotation(self):
        return self._rotation

    # public class-methods
    @classmethod
    def elements(cls):
        elements = list()
        translation_elements = cls.translation().axes()
        for element in translation_elements:
            padded = np.pad(element, [(1, 0), (0, 1)])
            elements.append(padded)
        rotation_elements = cls.rotation().elements()
        for element in rotation_elements:
            padded = np.pad(element, [(0, 1), (0, 1)])
            elements.append(padded)
        return elements

    # private static-methods
    @staticmethod
    def _construct_matrix(translation, rotation):
        pass

    # abstract properties
    @property
    @abstractmethod
    def n(self):
        pass

    @property
    @abstractmethod
    def m(self):
        pass

    # abstract implementations
    @classmethod
    def vector_to_algebra(cls, vector):
        assert isinstance(vector, Vector)
        elements = cls.elements()
        algebra = Square(np.zeros((n + 1, n + 1)))
        for index in range(n + m):
            algebra += vector[index] * elements[index]
        return algebra