from abc import ABC, abstractmethod


class Type(ABC):

    # public methods
    def to_string(self):
        return '{} {} {}'.format(self.tag(), self.id(), self.data_to_string())

    # private static-methods
    @staticmethod
    def _array_to_string(array):
        return ' '.join(['{:.6f}'.format(element) for element in array.flatten()])

    # abstract methods
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def data_to_string(self):
        pass

    @staticmethod
    @abstractmethod
    def tag():
        pass
