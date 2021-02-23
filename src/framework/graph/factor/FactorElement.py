from abc import ABC, abstractmethod
from typing import *


T = TypeVar('T')


class FactorElement(Generic[T], ABC):

    # constructor
    def __init__(self, value: Optional[T] = None, **kwargs):
        self._value: Optional[T] = value

    # getters/setters
    def get_value(self) -> T:
        assert self._value is not None
        return self._value

    def set_value(self, value: T):
        self._value = value

    # static properties
    @property
    @classmethod
    @abstractmethod
    def tag(cls) -> str:
        pass

    @property
    @classmethod
    @abstractmethod
    def is_physical(cls) -> bool:
        pass

    # write/read methods
    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def read(self, words: List[str]):
        pass
