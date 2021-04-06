import typing as tp
from abc import ABC

from src.framework.graph.protocols.ReadWrite import ReadWrite

T = tp.TypeVar('T')
SubData = tp.TypeVar('SubData', bound='Data')


class Data(tp.Generic[T], ReadWrite, ABC):
    """ A data-object that contains a value and value-type, which can be read and written. """

    _type: tp.Type[T]

    def __init__(
            self,
            value: tp.Optional[T] = None
    ):
        super().__init__()
        self._value: tp.Optional[T] = None
        if value is not None:
            self.set_value(value)

    # value
    def set_value(
            self,
            value: T
    ):
        """ Sets the value. """
        assert isinstance(value, self._type), f'Value <{value}> should be of type {self._type}.'
        self._value = value

    def get_value(self) -> T:
        """ Returns the value. """
        assert self.has_value()
        return self._value

    def has_value(self) -> bool:
        """ Returns whether a value is defined for this data-object. """
        return self._value is not None

    # type
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the value-type. """
        return cls._type
