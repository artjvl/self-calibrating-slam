import typing as tp
from abc import ABC, abstractmethod

from src.framework.graph.protocols.ReadWrite import ReadWrite
from src.framework.math.matrix.vector import SubVector

T = tp.TypeVar('T')
SubData = tp.TypeVar('SubData', bound='Data')


class Data(tp.Generic[T], ReadWrite, ABC):
    """ A data-object that contains a value and value-type, which can be read and written. """

    _type: tp.Type[T]
    _value: tp.Optional[T]

    def __init__(
            self,
            value: tp.Optional[T] = None
    ):
        super().__init__()
        self._value = None
        if value is not None:
            self.set_value(value)

    @abstractmethod
    def to_vector(self) -> SubVector:
        pass

    @abstractmethod
    def from_vector(self, vector: SubVector) -> None:
        pass

    # value
    def set_value(
            self,
            value: T
    ) -> None:
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

    # oplus
    @abstractmethod
    def oplus(self, delta: SubVector) -> T:
        """ Increments the value with a delta. """
        pass

    # type
    @classmethod
    def get_type(cls) -> tp.Type[T]:
        """ Returns the value-type. """
        return cls._type

    @classmethod
    @abstractmethod
    def get_dim(cls) -> int:
        """ Returns the dimension (i.e., minimal number of variables to fully define the data structure). """
        pass

    @classmethod
    def get_length(cls) -> int:
        return cls.get_dim()
