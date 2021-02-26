from abc import ABC, abstractmethod


class BaseElement(ABC):

    @abstractmethod
    def id_string(self) -> str:
        pass

    # object methods
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.id_string())

    def __repr__(self) -> str:
        return '{} <at {}>'.format(str(self), hex(id(self)))
