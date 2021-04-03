import typing as tp
from abc import abstractmethod

T = tp.TypeVar('T')


class Container(tp.Generic[T]):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_type(self) -> tp.Type[T]:
        pass

    @abstractmethod
    def get_value(self) -> T:
        pass
