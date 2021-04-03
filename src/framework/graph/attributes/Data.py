import typing as tp
from abc import ABC

from src.framework.graph.protocols.Container import Container
from src.framework.graph.protocols.ReadWrite import ReadWrite

T = tp.TypeVar('T')
SubData = tp.TypeVar('SubData', bound='Data')


class Data(Container[T], ReadWrite, ABC):
    _dimension: int

    def __init__(
            self,
            datatype: tp.Type[T],
            value: tp.Optional[T] = None
    ):
        super().__init__()
        self._datatype: tp.Type[T] = datatype
        self._value: tp.Optional[T] = None
        if value is not None:
            self.set_value(value)

    def set_value(
            self,
            value: T
    ):
        assert isinstance(value, self._datatype), f'Value <{value}> should be of type {self._datatype}.'
        self._value = value

    def get_value(self) -> T:
        assert self._value is not None, f'Internal value is None.'
        return self._value

    def get_type(self) -> tp.Type[T]:
        return self._datatype

    def get_word_count(self) -> int:
        return self._dimension
