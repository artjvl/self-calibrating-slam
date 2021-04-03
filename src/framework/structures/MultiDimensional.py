import typing as tp
from abc import abstractmethod

Sub = tp.TypeVar('Sub', bound='MultiDimensional')


class MultiDimensional(tp.Protocol):

    @abstractmethod
    def get_dimension(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def zeros(cls, dimension: int) -> Sub:
        pass

    @classmethod
    @abstractmethod
    def ones(cls, dimension: int) -> Sub:
        pass
